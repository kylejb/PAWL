"""Provide the Linkedin class."""
from . import service


class Linkedin:
    """The Linkedin class provides convenient access to Linkedin's API."""

    def __init__(self, access_token=None):
        self.me = service.Me(access_token)
        # self.auth = service.Auth()
