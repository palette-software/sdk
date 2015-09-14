import os
import sys
import unittest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(0, path)

import palette

URL = 'http://localhost:8080'

class TestBackup(unittest.TestCase):
    """ These tests assume a valid ~/.palette file."""
    def setUp(self):
        self.server = palette.connect(URL)
    def test_backup(self):
        self.server.backup()
    def test_query(self):
        backups = self.server.Backup.list_all(limit=3)
        self.assertTrue(backups)
        self.assertTrue(self.server.Backup.get(backups[0].unique_id))

if __name__ == '__main__':
    unittest.main()
