import logging
import random
import time
from copy import deepcopy
from urllib.parse import urljoin

from requests.status_codes import codes
from requests.exceptions import (
    ChunkedEncodingError,
    ConnectionError,
    ReadTimeout,
)

from .auth import BaseAuthorizer
from .rate_limit import RateLimiter
from .constants import TIMEOUT
from .exceptions import (
    BadJSON,
    BadRequest,
    Conflict,
    InvalidInvocation,
    NotFound,
    RequestException,
    ServerError,
    SpecialError,
    TooLarge,
    TooManyRequests,
    URITooLong,
)
from .util import authorization_error_class

log = logging.getLogger(__package__)


class RetryStrategy:
    """An abstract class for scheduling request retries.

    The strategy controls both the number and frequency of retry attempts.
    Instances of this class are immutable.
    """

    def sleep(self):
        """Sleep until we are ready to attempt the request."""
        sleep_seconds = self._sleep_seconds()
        if sleep_seconds is not None:
            message = f"Sleeping: {sleep_seconds:0.2f} seconds prior to retry"
            log.debug(message)
            time.sleep(sleep_seconds)


class FiniteRetryStrategy(RetryStrategy):
    """A ``RetryStrategy`` that retries requests a finite number of times."""

    def _sleep_seconds(self):
        if self._retries < 3:
            base = 0 if self._retries == 2 else 2
            return base + 2 * random.random()
        return None

    def __init__(self, retries: int = 3):
        """Initialize the strategy.

        :param retries: Number of times to attempt a request.
        """
        self._retries = retries

    def consume_available_retry(self):
        """Allow one fewer retry."""
        return type(self)(self._retries - 1)

    def should_retry_on_failure(self):
        """Return ``True`` if and only if the strategy will allow another retry."""
        return self._retries > 1


class Session:
    """The low-level connection interface to Linkedin's API."""

    RETRY_EXCEPTIONS = (ChunkedEncodingError, ConnectionError, ReadTimeout)
    RETRY_STATUSES = {
        520,
        522,
        codes["bad_gateway"],
        codes["gateway_timeout"],
        codes["internal_server_error"],
        codes["service_unavailable"],
    }
    STATUS_EXCEPTIONS = {
        codes["bad_gateway"]: ServerError,
        codes["bad_request"]: BadRequest,
        codes["conflict"]: Conflict,
        codes["forbidden"]: authorization_error_class,
        codes["gateway_timeout"]: ServerError,
        codes["internal_server_error"]: ServerError,
        codes["media_type"]: SpecialError,
        codes["not_found"]: NotFound,
        codes["request_entity_too_large"]: TooLarge,
        codes["request_uri_too_large"]: URITooLong,
        codes["service_unavailable"]: ServerError,
        codes["too_many_requests"]: TooManyRequests,
        codes["unauthorized"]: authorization_error_class,
        520: ServerError,
        522: ServerError,
    }
    SUCCESS_STATUSES = {codes["accepted"], codes["created"], codes["ok"]}

    @staticmethod
    def _log_request(data, method: str, params: dict, url: str):
        log.debug(f"Fetching: {method} {url}")
        log.debug(f"Data: {data}")
        log.debug(f"Params: {params}")

    def __init__(self, authorizer: BaseAuthorizer):
        """Prepare the connection to Linkedin's API.

        :param authorizer: An instance of :class:`Authorizer`.
        """
        if not isinstance(authorizer, BaseAuthorizer):
            raise InvalidInvocation(f"Invalid Authorizer: {authorizer}")
        self._authorizer = authorizer
        self._rate_limiter = RateLimiter()
        self._retry_strategy_class = FiniteRetryStrategy

    def __enter__(self):
        """Allow this object to be used as a context manager."""
        return self

    def __exit__(self, *_args):
        """Allow this object to be used as a context manager."""
        self.close()

    def _do_retry(
        self,
        data,
        json,
        method,
        params,
        response,
        retry_strategy_state,
        saved_exception,
        timeout,
        url,
    ):
        if saved_exception:
            status = repr(saved_exception)
        else:
            status = response.status_code
        log.warning(f"Retrying due to {status} status: {method} {url}")
        return self._request_with_retries(
            data=data,
            json=json,
            method=method,
            params=params,
            timeout=timeout,
            url=url,
            retry_strategy_state=retry_strategy_state.consume_available_retry(),  # noqa: E501
        )

    def _make_request(
        self,
        data,
        json,
        method,
        params,
        retry_strategy_state,
        timeout,
        url,
    ):
        try:
            response = self._rate_limiter.call(
                self._requestor.request,
                self._set_header_callback,
                method,
                url,
                allow_redirects=False,
                data=data,
                json=json,
                params=params,
                timeout=timeout,
            )
            log.debug(
                f"Response: {response.status_code}"
                f" ({response.headers.get('content-length')} bytes)"
            )
            return response, None
        except RequestException as exception:
            if (
                not retry_strategy_state.should_retry_on_failure()
                or not isinstance(  # noqa: E501
                    exception.original_exception, self.RETRY_EXCEPTIONS
                )
            ):
                raise
            return None, exception.original_exception

    def _request_with_retries(
        self,
        data,
        json,
        method,
        params,
        timeout,
        url,
        retry_strategy_state=None,
    ):
        if retry_strategy_state is None:
            retry_strategy_state = self._retry_strategy_class()

        retry_strategy_state.sleep()
        self._log_request(data, method, params, url)
        response, saved_exception = self._make_request(
            data,
            json,
            method,
            params,
            retry_strategy_state,
            timeout,
            url,
        )

        do_retry = False
        if response is not None and response.status_code == codes["unauthorized"]:
            self._authorizer._clear_access_token()
            if hasattr(self._authorizer, "refresh"):
                do_retry = True

        if retry_strategy_state.should_retry_on_failure() and (
            do_retry or response is None or response.status_code in self.RETRY_STATUSES
        ):
            return self._do_retry(
                data,
                json,
                method,
                params,
                response,
                retry_strategy_state,
                saved_exception,
                timeout,
                url,
            )
        elif response.status_code in self.STATUS_EXCEPTIONS:
            raise self.STATUS_EXCEPTIONS[response.status_code](response)
        elif response.status_code == codes["no_content"]:
            return
        assert (
            response.status_code in self.SUCCESS_STATUSES
        ), f"Unexpected status code: {response.status_code}"
        if response.headers.get("content-length") == "0":
            return ""
        try:
            return response.json()
        except ValueError:
            raise BadJSON(response)

    def _set_header_callback(self):
        if not self._authorizer.is_valid() and hasattr(self._authorizer, "refresh"):
            self._authorizer.refresh()
        return {
            "Authorization": f"Bearer {self._authorizer.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    @property
    def _requestor(self):
        return self._authorizer._authenticator._requestor

    def close(self):
        """Close the session and perform any clean up."""
        self._requestor.close()

    def request(
        self,
        method,
        path,
        data=None,
        json=None,
        params=None,
        timeout=TIMEOUT,
    ):
        """Return the json content from the resource at ``path``.

        :param method: The request verb. E.g., get, post, put.
        :param path: The path of the request. This path will be combined with the
            ``oauth_url`` of the Requestor.
        :param data: Dictionary, bytes, or file-like object to send in the body of the
            request.
        :param json: Object to be serialized to JSON in the body of the request.
        :param params: The query parameters to send with the request.
        Automatically refreshes the access token if it becomes invalid and a refresh
        token is available. Raises InvalidInvocation in such a case if a refresh token
        is not available.
        """
        # TODO - Fix params
        params = deepcopy(params) or {}
        if isinstance(data, dict):
            data = deepcopy(data)
            data = sorted(data.items())
        if isinstance(json, dict):
            json = deepcopy(json)
        url = urljoin(self._requestor.linkedin_url, path)
        return self._request_with_retries(
            data=data,
            json=json,
            method=method,
            params=params,
            timeout=timeout,
            url=url,
        )


def session(authorizer=None):
    """Return a :class:`Session` instance.

    :param authorizer: An instance of :class:`Authorizer`.
    """
    return Session(authorizer=authorizer)
