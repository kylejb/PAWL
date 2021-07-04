"""Provide the API's ServiceBase superclass."""
import requests


class ServiceBase:
    """Superclass for all services in `linkedin/api`."""

    def make_request(
        self, method, url, data=None, params=None, headers=None, timeout=60
    ):
        if headers is None:
            headers = {
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.authentication.token.access_token}",
            }
        else:
            headers.update(
                {
                    "X-Restli-Protocol-Version": "2.0.0",
                    "Content-Type": "application/json",
                }
            )
        kw = {"data": data, "params": params, "headers": headers, "timeout": timeout}
        return requests.request(method.upper(), url, **kw)
