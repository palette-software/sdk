import os
import sys
import unittest

# Force the tests to be performed in the order they are defined.
unittest.TestLoader.sortTestMethodsUsing = None

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(0, path)

import palette

URL = 'http://localhost:8080'

# The backup test is separate
class TestManageActions(unittest.TestCase):
    """ These tests assume a valid ~/.palette file."""
    def setUp(self):
        self.server = palette.connect(URL)

    def test_01_stop(self):
        self.server.stop()
    stop = test_01_stop

    def test_02_start(self):
        self.server.start()
    start = test_02_start

    def test_03_restart(self):
        self.server.restart()
    restart = test_03_restart

    def test_04_repair_license(self):
        self.server.repair_license()
    repair_license = test_04_repair_license

    def test_05_ziplogs(self):
        self.server.ziplogs()
    ziplogs = test_05_ziplogs

if __name__ == '__main__':
    unittest.main()
        
