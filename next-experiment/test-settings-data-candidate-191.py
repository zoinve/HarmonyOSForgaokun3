import json
from pathlib import Path
import runpy
import sqlite3
import tempfile
import unittest

API = runpy.run_path(str(Path(__file__).with_name('prepare-settings-data-candidate-191.py')))


class Tests(unittest.TestCase):
    def test_registry_owner_not_guessed(self):
        connection = sqlite3.connect(':memory:')
        try:
            connection.execute('CREATE TABLE installed_bundle (KEY TEXT, VALUE TEXT)')
            connection.execute('INSERT INTO installed_bundle VALUES (?, ?)', (
                'com.ohos.settingsdata', json.dumps(dict(singleton=True, bundleUserInfo=dict(userId=0),
                                                       uid=23456, accessTokenId=111))))
            self.assertEqual(API['settingsdata_uid'](connection), 23456)
        finally:
            connection.close()

    def test_missing_registry_owner_refused(self):
        connection = sqlite3.connect(':memory:')
        try:
            connection.execute('CREATE TABLE installed_bundle (KEY TEXT, VALUE TEXT)')
            with self.assertRaises(AssertionError):
                API['settingsdata_uid'](connection)
        finally:
            connection.close()

    def test_wrong_user_or_missing_singleton_refused(self):
        for singleton, user in [(True, 100), (False, 0)]:
            connection = sqlite3.connect(':memory:')
            try:
                connection.execute('CREATE TABLE installed_bundle (KEY TEXT, VALUE TEXT)')
                connection.execute('INSERT INTO installed_bundle VALUES (?, ?)', (
                    'com.ohos.settingsdata', json.dumps(dict(singleton=singleton,
                        bundleUserInfo=dict(userId=user), uid=23456, accessTokenId=111))))
                with self.assertRaises(AssertionError):
                    API['settingsdata_uid'](connection)
            finally:
                connection.close()

    def test_no_escape_or_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(API['safe_member'](root, 'app/file'), root / 'app/file')
            for path in ['../outside', '/etc/shadow']:
                with self.assertRaises(AssertionError):
                    API['safe_member'](root, path)
            (root / 'link').symlink_to('/tmp')
            with self.assertRaises(AssertionError):
                API['safe_member'](root, 'link/file')


if __name__ == '__main__':
    unittest.main()
