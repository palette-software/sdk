"""Exception classes for all Palette Errors."""

# apparently RequestException is a deep subclass...
# pylint: disable=too-many-ancestors

from requests.exceptions import RequestException

class PaletteError(RequestException):
    """Base class for all Palette exceptions."""
    def __init__(self, message, data=None):
        super(PaletteError, self).__init__(message)
        self.data = data

class PaletteInternalError(PaletteError):
    """Internal error."""
    pass

class PaletteAuthenticationError(PaletteError):
    """Authentication failure."""
    def __init__(self):
        msg = 'Invalid username or password'
        super(PaletteAuthenticationError, self).__init__(msg)

class PaletteJsonError(PaletteInternalError):
    """ Missing required key in JSON response """
    def __init__(self, key, data=None):
        message = "JSON data did not contain '{0}'".format(key)
        super(PaletteJsonError, self).__init__(message, data=data)
