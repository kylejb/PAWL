from typing import Union


def get_access_token(linkedin=None) -> str:
    from pawl.linkedin import Linkedin

    if linkedin is None or not isinstance(linkedin, Linkedin):
        raise ValueError("``linkedin`` was not provided.")
    url = linkedin.auth.url()
    print("Click here to provide authorization: ", url)

    redirected_url = input("Paste redirected URL from browser here: ")
    code = _get_code_from_raw_url(redirected_url)
    linkedin.auth.authorize(code)
    return linkedin._core._authorizer.access_token


def _get_code_from_raw_url(url) -> Union[str, None]:
    from urllib.parse import urlparse

    queries = urlparse(url).query.split("&")

    if len(queries) >= 1:
        for q in queries:
            query_key, query_value = q.split("=")[0], q.split("=")[1]
            if query_key == "code":
                return query_value
        raise RuntimeError("``code`` query was not found in the provided url")
