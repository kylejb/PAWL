"""Provides Authentication and Authorization classes."""


class BaseAuthenticator:
    """Provide the base authenticator object that stores OAuth2 credentials."""

    ...


class BaseAuthorizer:
    """Superclass for OAuth2 authorization tokens and scopes."""

    ...


class Authorizer(BaseAuthorizer):
    """Manages OAuth2 authorization tokens and scopes."""

    AUTHENTICATOR_CLASS = BaseAuthenticator

    def __init__(
        self,
        authenticator,
        post_refresh_callback=None,
        pre_refresh_callback=None,
        refresh_token=None,
    ):
        """Authorize access to Linkedin's API."""
        ...


class Authenticator(BaseAuthenticator):
    """Store OAuth2 authentication credentials for web, or script type apps."""

    ...
