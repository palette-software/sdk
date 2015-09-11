import os
import sys
import unittest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(0, path)

import palette

class TestConnectMethods(unittest.TestCase):
    """ These tests assume a valid ~/.palette file."""
    def test_basic(self):
        palette.connect('HTTP://localhost:8080/')
    def test_state(self):
        server = palette.connect('http://localhost:8080')
        self.assertIsNotNone(server.state)

if __name__ == '__main__':
    unittest.main()
        
