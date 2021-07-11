"""Provide `/authorization` service class."""
# import collections
import hashlib
import random

from enum import Enum

from .base import ServiceBase
from ..core import Authorizer, session

# AccessToken = collections.namedtuple("AccessToken", ["access_token", "expires_in"])


# TODO - Refactor permissions handling
class AuthPermissions(Enum):
    BASIC_PROFILE = "r_liteprofile"
    EMAIL_ADDRESS = "r_emailaddress"
    MEMBER_SOCIAL = "w_member_social"

    @staticmethod
    def to_oauth_scope():
        return [scope.value for scope in list(AuthPermissions)]


class Auth(ServiceBase):
    """Auth is a Service class that represents the `/authorization` endpoint."""

    def authorize(self, code: str):
        authenticator = self._linkedin._authorized_core._authorizer._authenticator
        authorizer = Authorizer(authenticator)
        authorizer.authorize(code)
        authorized_session = session.session(authorizer)
        self._linkedin._core = self._linkedin._authorized_core = authorized_session
        # TODO - create class for tokens
        return authorizer.access_token

    def url(
        self,
        scopes: list[str] = None,
        state: str = None,
    ) -> str:
        """Return the URL used out-of-band to grant access to your application."""
        authenticator = self._linkedin._authorized_core._authorizer._authenticator
        return authenticator.authorize_url(
            scopes=scopes or AuthPermissions.to_oauth_scope(),
            state=state or self._make_new_state(),
        )

    def _make_new_state(self):
        return hashlib.md5(
            "{}{}".format(
                random.randrange(0, 2 ** 63), self._linkedin._client_secret
            ).encode("utf8")
        ).hexdigest()

    # TODO - incorporate utils' raise for error into this class and extend to other objects?
    # def get_access_token(self, timeout=60):
    #     assert (
    #         self._linkedin._authorization_code
    #     ), "You must first get the authorization code"
    #     qd = {
    #         "grant_type": "authorization_code",
    #         "code": self._linkedin.authorization_code,
    #         "redirect_uri": self._linkedin.redirect_uri,
    #         "client_id": self._linkedin.client_id,
    #         "client_secret": self._linkedin.client_secret,
    #     }
    #     response = self.make_request(
    #         "POST", self.ACCESS_TOKEN_URL, data=qd, timeout=timeout
    #     )
    #     raise_for_error(response)
    #     response = response.json()
    #     self.access_token = AccessToken(
    #         response["access_token"], response["expires_in"]
    #     )
    #     return self.access_token
