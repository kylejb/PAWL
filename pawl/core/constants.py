"""Constants for core."""
import os

ACCESS_TOKEN_PATH = "v2/accessToken"
AUTHORIZATION_PATH = "v2/authorization"

TIMEOUT = float(os.environ.get("pawl_timeout", 16))
