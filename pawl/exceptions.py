class LinkedinError(Exception):
    pass


class LinkedinBadRequestError(LinkedinError):
    pass


class LinkedinUnauthorizedError(LinkedinError):
    pass


class LinkedinPaymentRequiredError(LinkedinError):
    pass


class LinkedinNotFoundError(LinkedinError):
    pass


class LinkedinConflictError(LinkedinError):
    pass


class LinkedinForbiddenError(LinkedinError):
    pass


class LinkedinInternalServiceError(LinkedinError):
    pass


ERROR_CODE_EXCEPTION_MAPPING = {
    400: LinkedinBadRequestError,
    401: LinkedinUnauthorizedError,
    402: LinkedinPaymentRequiredError,
    403: LinkedinForbiddenError,
    404: LinkedinNotFoundError,
    409: LinkedinForbiddenError,
    500: LinkedinInternalServiceError,
}


def get_exception_for_error_code(error_code):
    return ERROR_CODE_EXCEPTION_MAPPING.get(error_code, LinkedinError)
