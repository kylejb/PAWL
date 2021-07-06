from .exceptions import (
    ExpiredToken,
    Forbidden,
    InsufficientScope,
    InvalidToken,
    MissingToken,
    RevokedToken,
    UnknownAuthSchema,
)

_auth_error_mapping = {
    403: Forbidden,
    "insufficient_scope": InsufficientScope,
    "Invalid access token": InvalidToken,
    "Empty oauth2_access_token": MissingToken,
    "Expired access token": ExpiredToken,
    "The token has been revoked": RevokedToken,
    "Unknown authentication schema": UnknownAuthSchema,
}


def authorization_error_class(response):
    """Return an exception instance that maps to the OAuth2 Error.

    :param response: The HTTP response containing an authentication error.
    """
    error = response.json()
    if error:
        error = error["message"]
    else:
        error = response["status"]
    return _auth_error_mapping[error](response)
