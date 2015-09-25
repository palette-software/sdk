import os
import sys
import unittest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(0, path)

import palette

URL = 'http://localhost:8080'

class TestRestore(unittest.TestCase):
    """ These tests assume a valid ~/.palette file."""
    def setUp(self):
        self.server = palette.connect(URL)
    def test_backup(self):
        backup = self.server.backup()
        self.assertIn('url', backup)
    def test_restore(self):
        backups = self.server.Backup.list_all(limit=1)
        self.assertTrue(backups)
        self.server.restore(backups[0])
    def test_restore_data_only(self):
        backups = self.server.Backup.list_all(limit=1)
        self.assertTrue(backups)
        self.server.restore(backups[0], data_only=True)

if __name__ == '__main__':
    unittest.main()
