"""Provide `/me` service class."""
from .base import ServiceBase
from ..constants import API_PATH

# from ..utils.raise_for_error import raise_for_error


class Me(ServiceBase):
    """Me is a Service class that represents the `/me` endpoint."""

    def basic_profile(self):
        json_response = self._linkedin.get(path=f"v2/{API_PATH['me']}")

        """
        TODO - Refactor object structure
            - Return objects need to comform to module defined standards
            - Apply error handle on object as attribute
        """
        # raise_for_error(response)

        return json_response
