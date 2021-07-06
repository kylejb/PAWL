"""Provide exception classes for the Core package."""


class CoreException(Exception):
    """Base exception class for exceptions that occur within this package."""


class InvalidInvocation(CoreException):
    """Indicate that the code to execute cannot be completed."""


class RequestException(CoreException):
    """Indicate that there was an error with the incomplete HTTP request."""

    def __init__(self, original_exception, request_args, request_kwargs):
        """Initialize a RequestException instance.

        :param original_exception: The original exception that occurred.
        :param request_args: The arguments to the request function.
        :param request_kwargs: The keyword arguments to the request function.

        """
        self.original_exception = original_exception
        self.request_args = request_args
        self.request_kwargs = request_kwargs
        super(RequestException, self).__init__(
            f"error with request {original_exception}"
        )


class ResponseException(CoreException):
    """Indicate that there was an error with the completed HTTP request."""

    def __init__(self, response):
        """Initialize a ResponseException instance.

        :param response: A requests.response instance.

        """
        self.response = response
        super(ResponseException, self).__init__(
            f"received {response.status_code} HTTP response"
        )


class OAuthException(CoreException):
    """Indicate that there was an OAuth2 related error with the request."""

    def __init__(self, response, error, description):
        """Initialize a OAuthException instance.

        :param response: A requests.response instance.
        :param error: The error type returned by Linkedin.
        :param description: A description of the error when provided.

        """
        self.error = error
        self.description = description
        self.response = response
        message = f"{error} error processing request"
        if description:
            message += f" ({description})"
        CoreException.__init__(self, message)


class BadJSON(ResponseException):
    """Indicate the response did not contain valid JSON."""


class BadRequest(ResponseException):
    """Indicate invalid parameters for the request."""


class Conflict(ResponseException):
    """Indicate a conflicting change in the target resource."""


class ExpiredToken(ResponseException):
    """Indicate that the access token has expired."""


class Forbidden(ResponseException):
    """Indicate the authentication is not permitted for the request."""


class InsufficientScope(ResponseException):
    """Indicate that the request requires a different scope."""


class InvalidToken(ResponseException):
    """Indicate that the request used an invalid access token."""


class MissingToken(ResponseException):
    """Indicate that the request is missing an access token."""


class NotFound(ResponseException):
    """Indicate that the requested URL was not found."""


class RevokedToken(ResponseException):
    """Indicate that user's access token has been revoked by the member on Linkedin’s website."""


class ServerError(ResponseException):
    """Indicate issues on the server end preventing request fulfillment."""


class SpecialError(ResponseException):
    """Indicate syntax or spam-prevention issues."""

    def __init__(self, response):
        """Initialize a SpecialError exception instance.

        :param response: A requests.response instance containing a message and a list of
            special errors.

        """
        self.response = response

        resp_dict = self.response.json()  # assumes valid JSON
        self.message = resp_dict.get("message", "")
        self.reason = resp_dict.get("reason", "")
        self.special_errors = resp_dict.get("special_errors", [])
        CoreException.__init__(self, f"Special error {self.message!r}")


class TooLarge(ResponseException):
    """Indicate that the request data exceeds the allowed limit."""


class TooManyRequests(ResponseException):
    """Indicate that the user has sent too many requests in a given amount of time."""

    def __init__(self, response):
        """Initialize a TooManyRequests exception instance.

        :param response: A requests.response instance that may contain a retry-after
        header and a message.

        """
        self.response = response
        self.retry_after = response.headers.get("retry-after")
        self.message = response.text  # Not all response bodies are valid JSON

        msg = f"received {response.status_code} HTTP response"
        if self.retry_after:
            msg += (
                f". Please wait at least {float(self.retry_after)} seconds "
                "before re-trying this request."
            )
        CoreException.__init__(self, msg)


class UnknownAuthSchema(ResponseException):
    """Indicate unrecognized authentication header schema."""


class URITooLong(ResponseException):
    """Indicate that the length of the request URI exceeds the allowed limit."""
