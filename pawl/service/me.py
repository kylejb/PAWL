"""Provide `/me` service class."""
from .base import ServiceBase
from ..constants import API_PATH
from ..utils.raise_for_error import raise_for_error


class Me(ServiceBase):
    """Me is a Service class that represents the `/me` endpoint."""

    def __init__(self, access_token=None):
        self.access_token = access_token

    def get_basic_profile(self):
        response = self.make_request(
            "GET",
            f"https://api.linkedin.com/v2/{API_PATH['me']}",
            headers={"Authorization": "Bearer " + self.access_token},
        )
        raise_for_error(response)
        return response.json()
