"""Server classes for Palette"""
import urlparse
import ConfigParser as configparser

import requests

from .config import PARSER, SECTION_CREDENTIALS
from .error import PaletteError
from .error import PaletteAuthenticationError, PaletteInternalError

STATUS_KEY = 'status'
ERROR_KEY = 'error'
STATE_KEY = 'state'

def check_url(url):
    """Sanity check to ensure that the passed URL *may* represent
    a Palette Server instance.
    """
    parts = urlparse.urlsplit(url)
    if parts.scheme != 'http' and parts.scheme != 'https':
        raise ValueError("The url scheme must be 'http' or 'https'")
    if parts.path != '/' and parts.path != '':
        raise ValueError("The url path must be '/'")
    return urlparse.urlunsplit(parts)

def status_ok(data):
    """Check if the server responded with 'status: OK' in the JSON data.
    """
    if STATUS_KEY not in data:
        message = "JSON data did not contain '{0}'".format(STATUS_KEY)
        raise PaletteInternalError(message, data=data)

    if data[STATUS_KEY] == 'OK':
        return True
    return False

def raise_for_error(data):
    """Raise an exception if the JSON response contained an error."""
    if status_ok(data):
        del data[STATUS_KEY]
        return

    if not ERROR_KEY in data:
        message = "JSON data did not contain '{0}'".format(ERROR_KEY)
        raise PaletteInternalError(message, data=data)
    raise PaletteError(data[ERROR_KEY], data=data)


class PaletteServer(object):
    """An interface to a particular Palette Server. The values
    passed to the constructor override any corresponding values in ~/.palette.

    :param username: The Palette username to use for authentication
    :type username: str
    :param password: The password for `username`
    :type password: str
    :raises: ValueError
    """
    LOGIN_PATH_INFO = '/login/authenticate'

    STATE_PATH_INFO = '/api/v1/state'

    COOKIE_AUTH_TKT = 'auth_tkt'

    def __init__(self, url, username=None, password=None, security_token=None):
        """Initialize the instance with the given parameters."""
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

    @property
    def state(self):
        """ A string representing the current state of the environment.

        NOTE: This is a keyword value, not the status message in the UI.

        :returns: str -- the state of the environment.
        """
        data = self.get(self.STATE_PATH_INFO)
        return data[STATE_KEY]

    def authenticate(self):
        """Authenticate the user against this Palette server.

        :raises: PaletteAuthenticationError
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

    def get(self, url, params=None):
        """Send a GET request to the server and receives a JSON response back.
        This method should rarely be needed outside of internal use.

        :param url: The Palette Server URL
        :type url: str
        :param params: Any query string information
        :type params: dict
        :returns: dict -- the JSON response
        """
        cookies = {self.COOKIE_AUTH_TKT: self.auth_tkt}
        res = requests.get(self._url(url), params=params, cookies=cookies)
        res.raise_for_status()
        data = res.json()
        raise_for_error(data)
        return data

    def _url(self, path_info):
        """Build the full url for the specified path_info."""
        return urlparse.urljoin(self.url, path_info)


def connect(url, username=None, password=None, security_token=None):
    """Create a PaletteServer instance and authenticate

    :returns: a :class:`PaletteServer <palette.PaletteServer>` instance
    :raises: PaletteAuthenticationError, ValueError
    """
    server = PaletteServer(url, username=username, password=password,
                           security_token=security_token)
    server.authenticate()
    return server
