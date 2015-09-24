""" The Palette Python SDK.
"""
__version__ = '0.0.0' # PEP440 compliant
__maintainer__ = 'Palette Software'
__email__ = 'support@palette-software.com'
__url__ = 'http://www.palette-software.com'

import logging

# Example usage:
# >>> palette.logger.addHandler(logging.StreamHandler())
# >>> palette.logger.setLevel(logging.DEBUG)
logger = logging.getLogger('palette')
logger.addHandler(logging.NullHandler())

from .server import PaletteServer, connect
