"""Provides Authentication and Authorization classes."""
from enum import Enum
from requests import Request
from requests.status_codes import codes
import time
from urllib.parse import quote

from . import constants
from .exceptions import InvalidInvocation, ResponseException


class AuthPermissions(Enum):
    BASIC_PROFILE = "r_liteprofile"
    EMAIL_ADDRESS = "r_emailaddress"
    MEMBER_SOCIAL = "w_member_social"

    @staticmethod
    def to_oauth_scope():
        return (" ").join([scope.value for scope in list(AuthPermissions)])


class BaseAuthenticator:
    """Provide the base authenticator object that stores OAuth2 credentials."""

    def __init__(self, requestor, client_id, redirect_uri=None):
        self._requestor = requestor
        self.client_id = client_id
        self.redirect_uri = redirect_uri

    def _post(self, url, success_status=codes["ok"], **data):
        response = self._requestor.request(
            "POST",
            url,
            data=data,
            headers={
                "Connection": "close",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        if response.status_code != success_status:
            raise ResponseException(response)
        return response

    def authorize_url(self, scopes, state):
        """Return the URL used out-of-band to grant access to your application.

        :param scopes: A list of OAuth scopes to request authorization for.
        :param state: A string that will be reflected in the callback to
            ``redirect_uri``. Elements must be printable ASCII characters in the range
            0x20 through 0x7E inclusive. This value should be temporarily unique to the
            client for whom the URL was generated.
        """
        if self.redirect_uri is None:
            raise InvalidInvocation("redirect URI not provided")
        params = self._prepare_params(
            {
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "response_type": "code",
                "scope": " ".join(scopes),
                "state": state,
            }
        )
        url = self._requestor.oauth_url + constants.AUTHORIZATION_PATH
        request = Request("GET", f"{url}?{params}")
        return request.prepare().url

    @staticmethod
    def _prepare_params(params: dict[str]) -> str:
        """Handle scope spacing for Linkedin API.

        WIP
        """
        params_list = [f"{quote(key)}={quote(value)}" for key, value in params.items()]
        return "&".join(params_list)


class Authenticator(BaseAuthenticator):
    """Store OAuth2 authentication credentials for web, or script type apps."""

    RESPONSE_TYPE = "code"

    def __init__(self, requestor, client_id, client_secret, redirect_uri=None):
        super(Authenticator, self).__init__(requestor, client_id, redirect_uri)
        self.client_secret = client_secret


class BaseAuthorizer:
    """Superclass for OAuth2 authorization tokens and scopes."""

    def __init__(self, authenticator: Authenticator):
        self._authenticator = authenticator
        self._clear_access_token()
        self._validate_authenticator()

    def _clear_access_token(self):
        self._expiration_timestamp = None
        self.access_token = None

    def _validate_authenticator(self):
        if not isinstance(self._authenticator, self.AUTHENTICATOR_CLASS):
            raise InvalidInvocation(
                "Must use a authenticator of type"
                f" {self.AUTHENTICATOR_CLASS.__name__}."
            )

    def is_valid(self):
        """Return whether or not the Authorizer is ready to authorize requests.

        A ``True`` return value does not guarantee that the access_token is actually
        valid on the server side.
        """
        if self.access_token and self._expiration_timestamp is not None:
            return (
                self.access_token is not None
                and time.time() < self._expiration_timestamp
            )

    def _request_token(self, **data):
        url = self._authenticator._requestor.oauth_url + constants.ACCESS_TOKEN_PATH
        pre_request_time = time.time()
        response = self._authenticator._post(url, **data)

        # TODO - Create abstract payload class
        payload = response.json()
        self._expiration_timestamp = pre_request_time - 10 + payload["expires_in"]
        self.access_token = payload["access_token"]
        # Not supported
        # if "refresh_token" in payload:
        #     self.refresh_token = payload["refresh_token"]


class Authorizer(BaseAuthorizer):
    """Manages OAuth2 authorization tokens and scopes."""

    AUTHENTICATOR_CLASS = BaseAuthenticator

    def __init__(
        self,
        authenticator,
        post_access_callback=None,
        pre_access_callback=None,
        access_token=None,
    ):
        """Authorize access to Linkedin's API."""
        super(Authorizer, self).__init__(authenticator)
        self._post_access_callback = post_access_callback
        self._pre_access_callback = pre_access_callback
        self.access_token = access_token

    def authorize(self, code: str):
        """Obtain and set authorization tokens based on ``code``.

        :param code: The code obtained by an out-of-band authorization request to
            Linkedin.
        """
        if self._authenticator.redirect_uri is None:
            raise InvalidInvocation("redirect URI not provided")
        self._request_token(
            grant_type="authorization_code",
            code=code,
            client_id=self._authenticator.client_id,
            client_secret=self._authenticator.client_secret,
            redirect_uri=self._authenticator.redirect_uri,
        )

    # Refresh token flow only supported on certain Linkedin platforms
    # Reference: https://docs.microsoft.com/en-us/linkedin/shared/authentication/programmatic-refresh-tokens?context=linkedin/marketing/context # noqa
    def refresh(self):
        """WIP - call pre and post callback."""
        if self._pre_access_callback:
            self._pre_access_callback(self)
        if self.access_token is None:
            raise InvalidInvocation("access token not provided")
        # self._request_token(grant_type="code", access_token=self.access_token)
        if self._post_access_callback:
            self._post_access_callback(self)
