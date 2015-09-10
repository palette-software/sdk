"""Server classes for Palette"""
import urlparse
import ConfigParser as configparser

import requests

from .config import PARSER, SECTION_CREDENTIALS
from .error import PaletteAuthenticationError, PaletteInternalError

def check_url(url):
    """Sanity check to ensure that the passed URL *may* represent
    a Palette Server instance.

    Raises:
      ValueError: if a component of the URL is invalid.
    Returns:
      str: normalized version of the specified URL.
    """
    parts = urlparse.urlsplit(url)
    if parts.scheme != 'http' and parts.scheme != 'https':
        raise ValueError("The url scheme must be 'http' or 'https'")
    if parts.path != '/' and parts.path != '':
        raise ValueError("The url path must be '/'")
    return urlparse.urlunsplit(parts)

class PaletteServer(object):
    """An interface to a particular Palette Server."""

    LOGIN_PATH_INFO = '/login/authenticate'

    COOKIE_AUTH_TKT = 'auth_tkt'

    def __init__(self, url, username=None, password=None, security_token=None):
        """Initialize the instance with the given parameters.

        Arguments:
          username (str): the Palette username to use for authentication
          password (str): the password for username

        Raises:
          ValueError: if an argument is incorrect.
        """
        self.url = check_url(url)
        if username is None:
            try:
                self.username = PARSER.get(SECTION_CREDENTIALS, 'username')
            except configparser.Error:
                raise ValueError("'username' is required.")
        else:
            self.username = username
        if password is None:
            try:
                self.password = PARSER.get(SECTION_CREDENTIALS, 'password')
            except configparser.Error:
                raise ValueError("'password' is required.")
        else:
            self.password = password
        self.security_token = security_token
        self.auth_tkt = None

    def _url(self, path_info):
        """Build the full url for the specified path_info."""
        return urlparse.urljoin(self.url, path_info)

    def authenticate(self):
        """Authenticate the user against this Palette server.

        Raises:
          PaletteAuthenticationError
        """
        payload = {'username': self.username, 'password': self.password}
        res = requests.post(self._url(self.LOGIN_PATH_INFO),
                            data=payload,
                            allow_redirects=False)
        if res.status_code >= 400:
            # returns a 3xx status code (redirect) on success
            raise PaletteAuthenticationError()
        if self.COOKIE_AUTH_TKT not in res.cookies:
            raise PaletteInternalError("'auth_tkt' is missing from response.")
        self.auth_tkt = res.cookies[self.COOKIE_AUTH_TKT]


def connect(url, username=None, password=None, security_token=None):
    """Create a PaletteServer instance and authenticate

    Returns:
      PaletteServer instance
    Raises:
      PaletteAuthenticationError: if the username or password is incorrect.
      ValueError: if an argument is incorrect.
    """
    server = PaletteServer(url, username=username, password=password,
                           security_token=security_token)
    server.authenticate()
    return server
