import os
import sys
import unittest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(0, path)

import palette

URL = 'http://localhost:8080'

class TestSystem(unittest.TestCase):
    """ These tests assume a valid ~/.palette file."""
    def setUp(self):
        self.server = palette.connect(URL)
    def test_list_all(self):
        data = self.server.System.list_all()
        self.assertTrue(data)
    def test_get(self):
        value = self.server.System.get('socket-timeout')
        self.assertTrue(isinstance(value, int))
    def test_save(self):
        value = self.server.System.get('socket-timeout')
        self.server.System.save('socket-timeout', 120)
        self.server.System.save('socket-timeout', value)
    def test_update(self):
        defaults = self.server.System.list_all()
        data = {}
        data['socket-timeout'] = 2 * defaults['socket-timeout']
        data['auto-update-enabled'] = not defaults['auto-update-enabled']
        self.server.System.update(data)
        data = {}
        data['socket-timeout'] = defaults['socket-timeout']
        data['auto-update-enabled'] = defaults['auto-update-enabled']
        self.server.System.update(data)
    def test_mapping(self):
        self.assertIn('socket-timeout', self.server.system)
        value = self.server.system['socket-timeout']
        self.server.system['socket-timeout'] = 2 * value
        self.server.system['socket-timeout'] = value

if __name__ == '__main__':
    unittest.main()
        
