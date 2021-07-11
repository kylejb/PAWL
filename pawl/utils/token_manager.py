"""Token management.

These classes were adapted from Bryce Boe's PRAW repository.

praw/utils/token_manager.py. PRAW, commit bb0e00025f4cf10be64469d8998cc6ae1d81ca8c, Bryce Boe, 2016.
"""
import sqlite3
from abc import ABC, abstractmethod


class BaseTokenManager(ABC):
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

    @abstractmethod
    def post_access_callback(self, authorizer):
        """Handle callback that is invoked after an access token is used."""
        raise NotImplementedError("``post_access_callback`` must be extended.")

    @abstractmethod
    def pre_access_callback(self, authorizer):
        """Handle callback that is invoked before an access token is used."""
        raise NotImplementedError("``pre_access_callback`` must be extended.")

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

        :param filename: The file the contains the access token.
        """
        super().__init__()
        self._filename = filename

    def post_access_callback(self, authorizer):
        """Update the saved copy of the access token."""
        with open(self._filename, "w") as fp:
            fp.write(authorizer.access_token)

    def pre_access_callback(self, authorizer):
        """Load the access token from the file."""
        if authorizer.access_token is None:
            with open(self._filename) as fp:
                authorizer.access_token = fp.read().strip()


class SQLiteTokenManager(BaseTokenManager):
    """Provides a SQLite3 based token manager.

    Unlike, :class:`.FileTokenManager`, the initial database need not be created ahead
    of time, as it'll automatically be created on first use. However, initial
    ``access_tokens`` will need to be registered via :meth:`.register` prior to use.
    See :ref:`sqlite_token_manager` for an example of use.
    .. warning::
        This class is untested on Windows because we encountered file locking issues in
        the test environment.
    """

    def __init__(self, database, key):
        """Load and save access tokens from a SQLite database.

        :param database: The path to the SQLite database.
        :param key: The key used to locate the ``access_token``. This ``key`` can be
            anything. You might use the ``client_id`` if you expect to have unique
            ``access_tokens`` for each ``client_id``.
        """
        super().__init__()
        self._connection = sqlite3.connect(database)
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS tokens (id, access_token, updated_at)"
        )
        self._connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_tokens_id on tokens(id)"
        )
        self._connection.commit()
        self.key = key

    def _get(self):
        cursor = self._connection.execute(
            "SELECT access_token FROM tokens WHERE id=?", (self.key,)
        )
        result = cursor.fetchone()
        if result is None:
            raise KeyError
        return result[0]

    def _set(self, access_token):
        """Set the access token in the database.

        This function will overwrite an existing value if the corresponding ``key``
        already exists.
        """
        self._connection.execute(
            "REPLACE INTO tokens VALUES (?, ?, datetime('now'))",
            (self.key, access_token),
        )
        self._connection.commit()

    def is_registered(self):
        """Return whether or not ``key`` already has a ``access_token``."""
        cursor = self._connection.execute(
            "SELECT access_token FROM tokens WHERE id=?", (self.key,)
        )
        return cursor.fetchone() is not None

    def post_access_callback(self, authorizer):
        """Update the access token in the database."""
        self._set(authorizer.access_token)

        # While the following line is not strictly necessary, it ensures that the
        # access token is not used elsewhere. And also forces the pre_access_callback
        # to always load the latest access_token from the database.
        authorizer.access_token = None

    def pre_access_callback(self, authorizer):
        """Load the access token from the database."""
        assert authorizer.access_token is None
        authorizer.access_token = self._get()

    def register(self, access_token):
        """Register the initial access token in the database.

        :returns: ``True`` if ``access_token`` is saved to the database, otherwise,
            ``False`` if there is already a ``access_token`` for the associated
            ``key``.
        """
        cursor = self._connection.execute(
            "INSERT OR IGNORE INTO tokens VALUES (?, ?, datetime('now'))",
            (self.key, access_token),
        )
        self._connection.commit()
        return cursor.rowcount == 1
