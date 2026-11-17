"""Offline checks for minimal seed ancestry and unrelated-row verification."""
from pathlib import Path
import runpy
import sqlite3
import unittest

BASE = Path(__file__).resolve().parent
api = runpy.run_path(str(BASE / 'prepare-oobe-seed-123-remote.py'))


class SeedChecks(unittest.TestCase):
    def test_every_parent_precedes_child(self):
        relative = Path('app/el1/0/database/com.ohos.settingsdata/entry/rdb')
        paths = api['ancestors'](relative)
        self.assertEqual(paths[0], Path('app'))
        self.assertEqual(paths[-1], relative)
        for parent, child in zip(paths, paths[1:]):
            self.assertEqual(child.parent, parent)

    def test_only_setup_rows_are_exempt(self):
        db = sqlite3.connect(':memory:')
        try:
            for table in ('SETTINGSDATA', 'USER_SETTINGSDATA_SECURE_100', 'USER_SETTINGSDATA_100'):
                db.execute('CREATE TABLE "' + table + '" (ID INTEGER PRIMARY KEY AUTOINCREMENT, KEYWORD TEXT UNIQUE, VALUE TEXT)')
            db.execute("INSERT INTO SETTINGSDATA (KEYWORD,VALUE) VALUES ('device_provisioned','0')")
            db.execute("INSERT INTO SETTINGSDATA (KEYWORD,VALUE) VALUES ('unrelated','keep')")
            before = api['content_without_setup'](db)
            db.execute("UPDATE SETTINGSDATA SET VALUE='1' WHERE KEYWORD='device_provisioned'")
            db.execute("INSERT INTO USER_SETTINGSDATA_SECURE_100 (KEYWORD,VALUE) VALUES ('user_setup_complete','1')")
            self.assertEqual(before, api['content_without_setup'](db))
            db.execute("UPDATE SETTINGSDATA SET VALUE='changed' WHERE KEYWORD='unrelated'")
            self.assertNotEqual(before, api['content_without_setup'](db))
        finally:
            db.close()

    def test_remote_source_compiles(self):
        compile((BASE / 'prepare-oobe-seed-123-remote.py').read_text(), 'seed123', 'exec')


if __name__ == '__main__':
    unittest.main()
