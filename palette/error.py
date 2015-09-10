"""Exception classes for all Palette Errors."""

class PaletteError(StandardError):
    """Base class for all Palette exceptions."""
    pass

class PaletteInternalError(PaletteError):
    """Internal error for the Palette Server."""
    pass

class PaletteAuthenticationError(PaletteError):
    """Authentication failure."""
    def __init__(self):
        super(PaletteAuthenticationError, self).__init__()
        self.message = 'Invalid username or password'
