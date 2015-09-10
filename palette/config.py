""" Configuration settings for the SDK """

import os
from ConfigParser import SafeConfigParser

SECTION_CREDENTIALS = 'Credentials'

PARSER = SafeConfigParser()
if 'HOME' in os.environ:
    PARSER.read(os.path.abspath(os.path.expanduser('~/.palette')))
