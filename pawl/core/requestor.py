"""Provides the HTTP request handling interface."""
import requests

from typing import Union

from .constants import TIMEOUT
from .exceptions import RequestException
from .session import Session


class Requestor:
    """Requestor provides an interface to HTTP requests."""

    def __getattr__(self, attribute):
        """Pass all undefined attributes to the _http attribute."""
        if attribute.startswith("__"):
            raise AttributeError
        return getattr(self._http, attribute)

    def __init__(
        self,
        oauth_url: str = "https://www.linkedin.com/oauth/",
        linkedin_url: str = "https://api.linkedin.com/",
        session: Union[Session, requests.Session, None] = None,
    ):
        """Create an instance of the Requestor class.

        :param oauth_url: (Optional) The URL used to make OAuth requests to the linkedin
            site. (Default: https://oauth.linkedin.com)
        :param linkedin_url: (Optional) The URL used when obtaining access tokens.
            (Default: https://www.linkedin.com)
        :param session: (Optional) A session to handle requests, compatible with
            requests.Session(). (Default: None)
        """
        self._http = session or requests.Session()
        self._http.headers["User-Agent"] = "pawl/0.0.2"
        self.oauth_url = oauth_url
        self.linkedin_url = linkedin_url

    def close(self):
        """Call close on the underlying session."""
        return self._http.close()

    def request(self, *args, timeout=TIMEOUT, **kwargs):
        """Issue the HTTP request capturing any errors that may occur."""
        try:
            return self._http.request(*args, timeout=timeout, **kwargs)
        except Exception as exc:
            raise RequestException(exc, args, kwargs)
