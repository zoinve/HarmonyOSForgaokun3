import json
from pathlib import Path
import runpy
import sqlite3
import unittest

API = runpy.run_path(str(Path(__file__).with_name('audit-settings-seed-db-185.py')))


class Tests(unittest.TestCase):
    def test_encrypted_not_opened(self):
        self.assertFalse(API['inspect_database'](b'not SQLite')['sqlite_header'])

    def test_selection(self):
        prefix = './.hmos-data/service/el1/public/bms/bundle_manager_service/'
        self.assertTrue(API['selected_database'](prefix + 'bmsdb.db'))
        self.assertFalse(API['selected_database'](prefix + 'bmsdb.db-wal'))

    def test_only_metadata_exported(self):
        connection = sqlite3.connect(':memory:')
        try:
            connection.execute('CREATE TABLE bundles (key TEXT, value TEXT)')
            connection.execute('INSERT INTO bundles VALUES (?, ?)', (
                'com.huawei.hmos.settings', json.dumps(dict(
                    bundleName='com.huawei.hmos.settings', versionName='fixture',
                    accessTokenId='PRIVATE_FIXTURE'))))
            connection.commit()
            result = API['inspect_database'](connection.serialize())
        finally:
            connection.close()
        self.assertEqual(result['tables'][0]['row_count'], 1)
        self.assertEqual(len(result['tables'][0]['settings_matches']), 1)
        self.assertNotIn('PRIVATE_FIXTURE', json.dumps(result))

    def test_wal_normalization_requires_empty_wal(self):
        connection = sqlite3.connect(':memory:')
        try:
            connection.execute('CREATE TABLE fixture (key TEXT)')
            original = connection.serialize()
        finally:
            connection.close()
        wal_header = original[:18] + b'\x02\x02' + original[20:]
        with self.assertRaises(AssertionError):
            API['inspect_database'](wal_header)
        result = API['inspect_database'](wal_header, empty_wal_verified=True)
        self.assertTrue(result['memory_only_journal_header_normalized'])
        self.assertEqual(wal_header[18:20], b'\x02\x02')


if __name__ == '__main__':
    unittest.main()
