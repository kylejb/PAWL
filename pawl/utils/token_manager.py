"""Token management.

These classes were adapted from Bryce Boe's PRAW repository.

praw/utils/token_manager.py. PRAW, commit bb0e00025f4cf10be64469d8998cc6ae1d81ca8c, Bryce Boe, 2016.
"""


class BaseTokenManager:
    """An abstract class for all token managers."""

    def __init__(self):
        """Prepare attributes needed by all token manager classes."""
        self._linkedin = None

    @property
    def linkedin(self):
        """Return the :class:`.Linkedin` instance bound to the token manager."""
        return self._linkedin

    @linkedin.setter
    def linkedin(self, value):
        if self._linkedin is not None:
            raise RuntimeError(
                "``Linkedin`` can only be set once and is done automatically"
            )
        self._linkedin = value

    def post_refresh_callback(self, authorizer):
        """Handle callback that is invoked after a refresh token is used."""
        raise NotImplementedError("``post_refresh_callback`` must be extended.")

    def pre_refresh_callback(self, authorizer):
        """Handle callback that is invoked before refreshing Linkedin's authorization."""
        raise NotImplementedError("``pre_refresh_callback`` must be extended.")


class FileTokenManager(BaseTokenManager):
    """Provides a trivial single-file based token manager."""

    def __init__(self, filename):
        """Load and save refresh tokens from a file.

        :param filename: The file the contains the refresh token.
        """
        super().__init__()
        self._filename = filename

    def post_refresh_callback(self, authorizer):
        """Update the saved copy of the refresh token."""
        with open(self._filename, "w") as fp:
            fp.write(authorizer.refresh_token)

    def pre_refresh_callback(self, authorizer):
        """Load the refresh token from the file."""
        if authorizer.refresh_token is None:
            with open(self._filename) as fp:
                authorizer.refresh_token = fp.read().strip()
