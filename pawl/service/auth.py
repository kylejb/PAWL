"""Provide `/authorization` service class."""
import collections
import hashlib
import random
import requests

from urllib.parse import quote

from .base import ServiceBase
from ..utils import raise_for_error

AccessToken = collections.namedtuple("AccessToken", ["access_token", "expires_in"])


class Auth(ServiceBase):
    """Auth is a Service class that represents the `/authorization` endpoint."""

    """Implement a standard OAuth 2.0 flow."""

    AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
    ACCESS_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

    def __init__(self, key, secret, redirect_uri, permissions=None):
        self.key = key
        self.secret = secret
        self.redirect_uri = redirect_uri
        self.permissions = permissions or []
        self.state = None
        self.authorization_code = None
        self.token = None
        self._error = None

    @property
    def authorization_url(self):
        qd = {
            "response_type": "code",
            "client_id": self.key,
            "scope": (" ".join(self.permissions)).strip(),
            "state": self.state or self._make_new_state(),
            "redirect_uri": self.redirect_uri,
        }

        qsl = ["%s=%s" % (quote(k), quote(v)) for k, v in qd.items()]
        return "%s?%s" % (self.AUTHORIZATION_URL, "&".join(qsl))

    @property
    def last_error(self):
        return self._error

    def _make_new_state(self):
        return hashlib.md5(
            "{}{}".format(random.randrange(0, 2 ** 63), self.secret).encode("utf8")
        ).hexdigest()

    def get_access_token(self, timeout=60):
        assert self.authorization_code, "You must first get the authorization code"
        qd = {
            "grant_type": "authorization_code",
            "code": self.authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.key,
            "client_secret": self.secret,
        }
        response = requests.post(self.ACCESS_TOKEN_URL, data=qd, timeout=timeout)
        raise_for_error(response)
        response = response.json()
        self.token = AccessToken(response["access_token"], response["expires_in"])
        return self.token
