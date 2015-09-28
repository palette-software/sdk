"""Server classes for Palette"""
import re
import urlparse
import ConfigParser as configparser
import requests

from urllib import urlencode

from .config import PARSER, SECTION_CREDENTIALS
from .error import PaletteAuthenticationError, PaletteInternalError

from . import logger
from .internal import ApiObject, JsonKeys, API_PATH_INFO, raise_for_json

class ManageActions(object):
    """Allowable actions for the 'manage' endpoint."""
    START = 'start'
    STOP = 'stop'
    RESTART = 'restart'
    BACKUP = 'backup'
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

def display_url(url, params=None):
    """Create a printable value for the url with optional query string.
    The output is primarily for debugging output.
    """
    if params:
        return url + '?' + urlencode(params)
    return url

def sanitize(data):
    """Return a string representation of the data with passwords removed."""
    data = data.copy()
    for key in data:
        if 'password' in key.lower():
            data[key] = re.sub('.', '*', data[key])
    return str(data)

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
    STATE_PATH_INFO = API_PATH_INFO + '/state'
    MANAGE_PATH_INFO = API_PATH_INFO + '/manage'

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

    def __getattr__(self, name):
        if name == 'Backup':
            from .backup import Backup
            return ApiObject(self, Backup)
        if name == 'System':
            from .system import System
            return ApiObject(self, System)
        if name == 'system':
            from .system import SystemMapping
            return SystemMapping(self)

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
        logger.debug('POST ' + self.LOGIN_PATH_INFO + ' ' + sanitize(payload))

        url = self._url(self.LOGIN_PATH_INFO)
        res = requests.post(url, data=payload, allow_redirects=False)
        logger.debug(str(res.status_code) + ' ' + str(res.reason))

        if res.status_code >= 400:
            # returns a 3xx status code (redirect) on success
            raise PaletteAuthenticationError()
        if self.COOKIE_AUTH_TKT not in res.cookies:
            raise PaletteInternalError("'auth_tkt' is missing from response.")
        self.auth_tkt = res.cookies[self.COOKIE_AUTH_TKT]
        logger.info("Authenticated username '%s'", self.username)

    def _manage(self, action, sync=True):
        """Perform a generic 'manage' operation on the server."""
        payload = {'action': action, 'sync': sync}
        return self.post(self.MANAGE_PATH_INFO, data=payload)

    def start(self, sync=True):
        """Start the Tableau server.

        :param sync: whether or not to wait for the action to complete.
        :type sync: bool
        :returns: True
        :raises: HTTPError
        """
        self._manage(ManageActions.START, sync=sync)
        if sync:
            logger.info("Tableau server started.")
        else:
            logger.info("Tableau server starting...")
        return True

    def stop(self, sync=True):
        """Stop the Tableau server.

        :param sync: whether or not to wait for the action to complete.
        :type sync: bool
        :returns: True
        :raises: HTTPError
        """
        self._manage(ManageActions.STOP, sync=sync)
        if sync:
            logger.info("Tableau server stopped.")
        else:
            logger.info("Tableau server stopping...")
        return True

    def restart(self, sync=True):
        """Restart the Tableau server.

        :param sync: whether or not to wait for the action to complete.
        :type sync: bool
        :returns: True
        :raises: HTTPError
        """
        self._manage(ManageActions.RESTART, sync=sync)
        if sync:
            logger.info("Tableau server restarted.")
        else:
            logger.info("Tableau server restarting...")
        return True


    def backup(self, sync=True):
        """Take a Tableau backup.

        :param sync: whether or not to wait for the action to complete.
        :type sync: bool
        :returns: a Backup instance or True if asynchronous (sync == False)
        :raises: HTTPError
        """
        data = self._manage(ManageActions.BACKUP, sync=sync)
        if not sync:
            logger.info("Backup in progress...")
            return True

        result = self.Backup.from_json(data)
        logger.info("Backup completed '%d': %s", data['id'], data['url'])
        return result

    def restore(self, backup, data_only=False, password=None, sync=True):
        """Restore Tableau from a tsbak file.

        :param backup: the Backup instance or URL of the file.
        :type path: str
        :param data_only: restore only data and not config.
        :type data_only: bool
        :param password: The tableau run-as-user-password (if needed)
        :type password: str
        :param sync: whether or not to wait for the action to complete.
        :type sync: bool
        :returns: True
        :raises: HTTPError
        """
        if not isinstance(backup, basestring):
            backup = backup.url
        elif not backup or not isinstance(backup, basestring):
            raise ValueError("Invalid 'backup' specified.")
        payload = {'action': 'restore', 'url': backup, 'sync': sync}
        if password:
            payload['password'] = password
        if data_only:
            payload['data-only'] = data_only
        self.post(self.MANAGE_PATH_INFO, data=payload)
        return True

    def repair_license(self, sync=True):
        """Repair the Tableau Server license.
        This effectively runs 'tabadmin licenses --repair_service'

        :param sync: whether or not to wait for the action to complete.
        :type sync: bool
        :returns: True
        :raises: HTTPError
        """
        self._manage(ManageActions.REPAIR_LICENSE, sync=sync)
        if sync:
            logger.info("License repair completed")
        else:
            logger.info("License repair in progress...")
        return True

    def ziplogs(self, sync=True):
        """Cleanup the Tableau Server logs.
        This effectively runs 'tabadmin ziplogs'

        :param sync: whether or not to wait for the action to complete.
        :type sync: bool
        :returns: True
        :raises: HTTPError
        """
        # Return information about the resulting zip file (like backup)
        self._manage(ManageActions.ZIPLOGS, sync=sync)
        if sync:
            logger.info("Ziplogs completed")
        else:
            logger.info("Ziplogs in progress...")
        return True

    def get(self, url, params=None, required=None):
        """Send a GET request to the server and receives a JSON response back.
        This method should rarely be needed outside of internal use.

        :param url: The Palette Server URL
        :type url: str
        :param params: Any query string information
        :type params: dict
        :returns: dict -- the JSON response
        """
        cookies = {self.COOKIE_AUTH_TKT: self.auth_tkt}
        logger.debug('GET %s', display_url(url, params))
        res = requests.get(self._url(url), params=params, cookies=cookies)
        res.raise_for_status()
        json = res.json()
        logger.debug('%s %s %s', str(res.status_code), str(res.reason), json)
        raise_for_json(json, required=required)
        return json

    def post(self, url, data=None, required=None):
        """Send a POST request to the server and receives a JSON response back.
        This method should rarely be needed outside of internal use.

        :param url: The Palette Server URL
        :type url: str
        :param data: The data payload to send with the request
        :type data: dict
        :returns: dict -- the JSON response
        """
        cookies = {self.COOKIE_AUTH_TKT: self.auth_tkt}
        logger.debug('POST %s %s', url, sanitize(data))
        res = requests.post(self._url(url), data=data, cookies=cookies)
        res.raise_for_status()
        json = res.json()
        logger.debug('%s %s %s', str(res.status_code), str(res.reason), json)
        raise_for_json(json, required=required)
        return json

    def _url(self, path_info):
        """Build the full url for the specified path_info."""
        return urlparse.urljoin(self.url, path_info)


def connect(url, username=None, password=None, security_token=None):
    """Create a PaletteServer instance and authenticate.

    :returns: a :class:`PaletteServer <palette.PaletteServer>` instance
    :raises: PaletteAuthenticationError, ValueError
    """
    server = PaletteServer(url, username=username, password=password,
                           security_token=security_token)
    server.authenticate()
    logger.info("Connected to server '%s'", url)
    return server
