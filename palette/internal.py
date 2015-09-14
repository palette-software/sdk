""" Internal class that are not part of the API. """

import inspect

from .error import PaletteError, PaletteJsonError, PaletteInternalError

API_PATH_INFO = '/api/v1'

class ClassMethod(object):
    """Wrapper around an exposed class method."""
    def __init__(self, server, method):
        self.server = server
        self.method = method

    def __call__(self, *args, **kwargs):
        return self.method(self.server, *args, **kwargs)

class ApiObject(object):
    """Wrapper for exposing class methods of base classes from PaletteServer."""

    def __init__(self, server, cls):
        self.server = server
        self.cls = cls

    def __getattr__(self, name):
        # raises AttributeError if not found...
        method = getattr(self.cls, name)
        # test for a classmethod
        if inspect.ismethod(method) and method.__self__ is self.cls:
            return ClassMethod(self.server, method)
        fmt = "type object '{0}' has no classmethod '{1}'"
        raise AttributeError(fmt.format(self.cls.__name__, name))

class JsonKeys(object):
    """Allowable key name for JSON responses."""
    STATUS = 'status'
    ERROR = 'error'
    STATE = 'state'
    BACKUPS = 'backups'


def status_ok(data):
    """Check if the server responded with 'status: OK' in the JSON data.
    """
    if JsonKeys.STATUS not in data:
        message = "JSON data did not contain '{0}'".format(JsonKeys.STATUS)
        raise PaletteInternalError(message, data=data)

    if data[JsonKeys.STATUS] == 'OK':
        return True
    return False

def raise_for_json(data, required=None):
    """Raise an exception if the JSON response contained an error or
    was missing a required parameter."""
    if status_ok(data):
        del data[JsonKeys.STATUS]
    else:
        if not JsonKeys.ERROR in data:
            raise PaletteJsonError(JsonKeys.ERROR, data=data)
        raise PaletteError(data[JsonKeys.ERROR], data=data)

    if not required is None:
        if isinstance(required, basestring):
            required = (required, )
        for key in required:
            if not key in data:
                raise PaletteJsonError(key, data)
    return

def translate_to_variable_name(key):
    """Convert a 'pretty' JSON key to a valid variable name."""
    return key.replace('-', '_')
