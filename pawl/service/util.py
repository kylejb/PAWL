import requests

from ..exceptions import LinkedinError, get_exception_for_error_code


def raise_for_error(response):
    try:
        response.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError) as error:
        try:
            if len(response.content) == 0:
                # There is nothing we can do here since Linkedin has neither sent
                # us a 2xx response nor a response content.
                return
            response = response.json()
            if ("error" in response) or ("errorCode" in response):
                message = "%s: %s" % (
                    response.get("error", str(error)),
                    response.get("message", "Unknown Error"),
                )
                error_code = response.get("status")
                ex = get_exception_for_error_code(error_code)
                raise ex(message)
            else:
                raise LinkedinError(error.message)
        except (ValueError, TypeError):
            raise LinkedinError(error.message)
