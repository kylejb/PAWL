"""Provide the Linkedin class."""
from typing import Optional, Union, IO, Any, Dict, List

from . import service
from .core.auth import Authorizer, Authenticator  # noqa
from .core.requestor import Requestor
from .core.session import session


class Linkedin:
    """The Linkedin class provides convenient access to Linkedin's API."""

    def __init__(
        self,
        access_token=None,
        client_id=None,
        client_secret=None,
        redirect_uri="http://localhost:8000",
        token_manager=None,
    ):
        assert access_token or (
            client_id and client_secret
        ), "Either client_id and client_secret or an access token is required."

        self._core = self._authorized_core = None

        # TODO - Abstract these values for security
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        # TODO END

        self._services = None
        self._token_manager = token_manager

        self._map_services()
        self._prepare_core()

        self.auth = service.Auth(self, None)

        self.current_user = service.Me(linkedin=self, _data=None)
        self.current_user_id = self._set_linkedin_user_id()

        self.reactions = service.Reactions(linkedin=self, _data=None)

    def _prepare_core(self, requestor_class=None, requestor_kwargs=None):
        requestor_class = requestor_class or Requestor
        requestor_kwargs = requestor_kwargs or {}

        requestor = requestor_class()
        self._prepare_core_authenticator(requestor)

    def _prepare_core_authenticator(self, requestor):
        authenticator = Authenticator(
            requestor, self._client_id, self._client_secret, self._redirect_uri
        )
        self._prepare_core_authorizer(authenticator)

    def _prepare_core_authorizer(self, authenticator: Authenticator):
        if self._token_manager is not None:
            self._token_manager.linkedin = self
            authorizer = Authorizer(
                authenticator,
                post_access_callback=self._token_manager.post_access_callback,
                pre_access_callback=self._token_manager.pre_access_callback,
            )
        else:
            # TODO - Add error handling
            authorizer = Authorizer(authenticator)
        self._core = self._authorized_core = session(authorizer)

    def _map_services(self):
        service_mappings = {
            "Me": service.Me,
            "Reactions": service.Reactions,
        }
        self._services = service_mappings

    @staticmethod
    def _parse_service_request(data: Optional[Union[Dict[str, Any], List[Any], bool]]):
        # TODO - Restructure data for ease of use with python/utf-8
        return data

    def _service_request(
        self,
        data: Optional[Union[Dict[str, Union[str, Any]], bytes, IO, str]] = None,
        json=None,
        method: str = "",
        params: Optional[Union[str, Dict[str, str]]] = None,
        path: str = "",
    ) -> Any:
        """Run a request through mapped services.

        :param data: Dictionary, bytes, or file-like object to send in the body of the
            request (default: None).
        :param json: JSON-serializable object to send in the body of the request with a
            Content-Type header of application/json (default: None). If ``json`` is
            provided, ``data`` should not be.
        :param method: The HTTP method (e.g., GET, POST, PUT, DELETE).
        :param params: The query parameters to add to the request (default: None).
        :param path: The path to fetch.
        """
        return self._parse_service_request(
            data=self._core.request(
                data=data,
                json=json,
                method=method,
                params=params,
                path=path,
            )
        )

    def get(
        self,
        path: str,
        params: Optional[Union[str, Dict[str, Union[str, int]]]] = None,
    ):
        """Return parsed objects returned from a GET request to ``path``.

        :param path: The path to fetch.
        :param params: The query parameters to add to the request (default: None).
        """
        return self._service_request(method="GET", params=params, path=path)

    def post(
        self,
        path: str,
        data: Optional[Union[Dict[str, Union[str, Any]], bytes, IO, str]] = None,
        params: Optional[Union[str, Dict[str, Union[str, int]]]] = None,
        json=None,
    ):
        return self._service_request(
            data=data,
            json=json,
            method="POST",
            params=params,
            path=path,
        )

    def _set_linkedin_user_id(self):
        if self._authorized_core._authorizer.access_token is not None:
            return self.current_user.basic_profile()["id"]
        return None
