""" Classes and functions for handling Tableau Backups """
from __future__ import absolute_import
from .error import PaletteInternalError
from .internal import API_PATH_INFO, translate_to_variable_name

class Backup(object):
    """ A Tableau Server backup object.

    The classmethods of this class are most easily accessed via
    ```server.Backup.method(...)``  where `server` is a PaletteServer instance.

    >>> server = palette.connect(URL)
    >>> print server.Backup.list(limit=1)
    [<palette.backup.Backup object at 0x7f719714cc10>]

    """

    MAX_LIMIT = 100
    PATH_INFO = API_PATH_INFO + '/backups'

    def __init__(self, server, unique_id, data=None):
        # pylint: disable=redefined-builtin
        self.server = server
        self.unique_id = unique_id
        if not data is None:
            for key in data:
                if key == 'id':
                    continue
                name = translate_to_variable_name(key)
                setattr(self, name, data[key])

    @classmethod
    def from_json(cls, server, data):
        """ Convert a JSON object (as a dictionary) to an instance of `cls`.
        """
        if not 'id' in data:
            message = "JSON object '{0}' does not contain an 'id'"
            raise PaletteInternalError(message.format(cls.__name__))
        return cls(server, data['id'], data)

    @classmethod
    def get(cls, server, backup_id):
        """ Return information about a backup by unique id.

        :param server: The server instance
        :type username: PaletteServer
        :param backup_id: the unique identifier of a backup.
        :type backup_id: int
        :raises: HTTPError
        """
        path_info = cls.PATH_INFO + '/' + str(backup_id)
        return cls.from_json(server, server.get(path_info, required=('id')))

    @classmethod
    def list_all(cls, server, limit=7, desc=True):
        """ Return a list of available backups.

        :param server: The server instance
        :type username: PaletteServer
        :param limit: the maximum number of backup instances returned (max=100).
        :type limit: int
        :param desc: sort descending or not
        :type desc: bool
        :raises: ValueError, HTTPError
        """
        if limit > cls.MAX_LIMIT:
            fmt = "The value of 'limit' must be less than or equal to {0}'"
            raise ValueError(fmt.format(cls.MAX_LIMIT))
        params = {'limit': int(limit), 'desc': desc}
        json = server.get(cls.PATH_INFO, params=params, required=('backups'))

        backups = []
        for obj in json['backups']:
            backups.append(cls.from_json(server, obj))
        return backups
