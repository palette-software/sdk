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
        super(PaletteAuthenticationError, self).__init__()
        self.message = 'Invalid username or password'
