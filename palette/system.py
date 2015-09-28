""" Classes and functions for handling the Palette system table """
from __future__ import absolute_import
from .internal import API_PATH_INFO, DictObject

class System(DictObject):
    """ The low-level Palette Server system table interface.

    ``server.system`` provides a more convienent, mapping-like interface
    to the system table.

    >>> print server.system['backup-user-retain-count']
    1
    >>> server.system['backup-user-retain-count'] = 3
    >>> print server.system['backup-user-retain-count']
    3

    """
    # pylint: disable=too-many-public-methods
    PATH_INFO = API_PATH_INFO + '/system'

    @classmethod
    def get(cls, server, key):
        """ Return the value of a particular system table key.
        :param server: The server instance
        :type server: PaletteServer
        :param key: the system table key
        :type key: str
        :return: the (typed) value of the specified key
        :raises: HTTPError
        """
        path_info = cls.PATH_INFO + '/' + str(key)
        data = server.get(path_info, required=('value'))
        return data['value']

    @classmethod
    def list_all(cls, server):
        """ Return the entire contents of the system table as a mapping.
        :param server: The server instance
        :type server: PaletteServer
        :return: mapping of key-value pairs
        :raises: HTTPError
        """
        return server.get(cls.PATH_INFO)

    @classmethod
    def update(cls, server, data):
        """ Set values for specified keys in the system table.
        :param server: The server instance
        :type server: PaletteServer
        :param data: a key-value mapping of data to be set
        :type data: dict
        :raises: HTTPError
        """
        server.post(cls.PATH_INFO, data=data)

    @classmethod
    def save(cls, server, key, value):
        """ Set the value for one key in the system table.
        :param server: The server instance
        :type server: PaletteServer
        :param key: the system table key
        :type key: str
        :param value: the new value (typed)
        :raises: HTTPError
        """
        path_info = cls.PATH_INFO + '/' + str(key)
        server.post(path_info, data={'value': value})


class SystemMapping(dict):
    """ Interface to the system table that acts like a standard dict() """

    def __init__(self, server):
        self.server = server
        data = server.System.list_all()
        dict.__init__(self, data)

    def __setitem__(self, key, value):
        self.server.System.save(key, value)
        dict.__setitem__(self, key, value)
