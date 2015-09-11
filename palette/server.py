"""Server classes for Palette"""
import urlparse
import ConfigParser as configparser

import requests

from .config import PARSER, SECTION_CREDENTIALS
from .error import PaletteError
from .error import PaletteAuthenticationError, PaletteInternalError

class JsonKeys(object):
    """Allowable key name for JSON responses."""
    STATUS = 'status'
    ERROR = 'error'
    STATE = 'state'

class ManageActions(object):
    """Allowable actions for the 'manage' endpoint."""
    START = 'start'
    STOP = 'stop'
    RESTART = 'restart'
    REPAIR_LICENSE = 'repair-license'
    ZIPLOGS = 'ziplogs'

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
    if JsonKeys.STATUS not in data:
        message = "JSON data did not contain '{0}'".format(JsonKeys.STATUS)
        raise PaletteInternalError(message, data=data)

    if data[JsonKeys.STATUS] == 'OK':
        return True
    return False

def raise_for_error(data):
    """Raise an exception if the JSON response contained an error."""
    if status_ok(data):
        del data[JsonKeys.STATUS]
        return

    if not JsonKeys.ERROR in data:
        message = "JSON data did not contain '{0}'".format(JsonKeys.ERROR)
        raise PaletteInternalError(message, data=data)
    raise PaletteError(data[JsonKeys.ERROR], data=data)


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
    MANAGE_PATH_INFO = '/api/v1/manage'

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
        return data[JsonKeys.STATE]

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

    def _manage(self, action, sync=True):
        """Perform a generic 'manage' operation on the server."""
        payload = {'action': action, 'sync': sync}
        self.post(self.MANAGE_PATH_INFO, data=payload)
        return True

    def start(self, sync=True):
        """Start the Tableau server.

        :param sync: whether or not to wait for the action to complete.
        :type sync: bool
        :returns: True
        :raises: HTTPError
        """
        return self._manage(ManageActions.START, sync=sync)

    def stop(self, sync=True):
        """Stop the Tableau server.

        :param sync: whether or not to wait for the action to complete.
        :type sync: bool
        :returns: True
        :raises: HTTPError
        """
        return self._manage(ManageActions.STOP, sync=sync)

    def restart(self, sync=True):
        """Restart the Tableau server.

        :param sync: whether or not to wait for the action to complete.
        :type sync: bool
        :returns: True
        :raises: HTTPError
        """
        return self._manage(ManageActions.RESTART, sync=sync)

    def repair_license(self, sync=True):
        """Repair the Tableau Server license.
        This effectively runs 'tabadmin licenses --repair_service'

        :param sync: whether or not to wait for the action to complete.
        :type sync: bool
        :returns: True
        :raises: HTTPError
        """
        return self._manage(ManageActions.REPAIR_LICENSE, sync=sync)

    def ziplogs(self, sync=True):
        """Cleanup the Tableau Server logs.
        This effectively runs 'tabadmin ziplogs'

        :param sync: whether or not to wait for the action to complete.
        :type sync: bool
        :returns: True
        :raises: HTTPError
        """
        return self._manage(ManageActions.ZIPLOGS, sync=sync)

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
        json = res.json()
        raise_for_error(json)
        return json

    def post(self, url, data=None):
        """Send a POST request to the server and receives a JSON response back.
        This method should rarely be needed outside of internal use.

        :param url: The Palette Server URL
        :type url: str
        :param data: The data payload to send with the request
        :type data: dict
        :returns: dict -- the JSON response
        """
        cookies = {self.COOKIE_AUTH_TKT: self.auth_tkt}
        res = requests.post(self._url(url), data=data, cookies=cookies)
        res.raise_for_status()
        json = res.json()
        raise_for_error(json)
        return json

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
