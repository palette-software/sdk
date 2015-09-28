""" Classes and functions for handling Tableau Backups """
from __future__ import absolute_import
from .internal import API_PATH_INFO, DictObject

class Backup(DictObject):
    """ A Tableau Server backup object.

    The classmethods of this class are most easily accessed via
    ```server.Backup.method(...)``  where `server` is a PaletteServer instance.

    >>> server = palette.connect(URL)
    >>> print server.Backup.list_all(limit=1)
    [{u'id': 56, ...}]

    Backup instances are mapping objects so the properties may be easily
    inspected:

    >>> from pprint import pprint
    >>> pprint(backup)
    {u'id': 56,
     u'url': u's3://test-palette-com/tableau-backups/20150924_155401.tsbak',
     u'size': 6586553,
     u'creation-time': u'2015-09-24T22:55:17.861285Z'}

    """

    MAX_LIMIT = 100
    PATH_INFO = API_PATH_INFO + '/backups'

    @classmethod
    def get(cls, server, backup_id):
        """ Return information about a backup by unique id.

        :param server: The server instance
        :type server: PaletteServer
        :param backup_id: the unique identifier of a backup.
        :type backup_id: int
        :return: the backup
        :rtype: Backup instance
        :raises: HTTPError
        """
        path_info = cls.PATH_INFO + '/' + str(backup_id)
        return cls.from_json(server, server.get(path_info, required=('id')))

    @classmethod
    def list_all(cls, server, limit=7, desc=True):
        """ Return a list of available backups.

        :param server: The server instance
        :type server: PaletteServer
        :param limit: the maximum number of backup instances returned (max=100).
        :type limit: int
        :param desc: sort descending or not
        :type desc: bool
        :return: the available backups
        :rtype: list of Backup instances
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
