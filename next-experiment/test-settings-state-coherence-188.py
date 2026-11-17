import json
from pathlib import Path
import runpy
import sqlite3
import unittest

API = runpy.run_path(str(Path(__file__).with_name('audit-settings-state-coherence-188.py')))
BUNDLE = API['BUNDLE']


class Tests(unittest.TestCase):
    def test_explicit_hap_abi_mapping(self):
        self.assertEqual(API['CODE'][API['PUBLIC'] + 'libs/arm64/libnative.so'],
                         'libs/arm64-v8a/libnative.so')

    def test_bms_bundle_and_user_scope(self):
        connection = sqlite3.connect(':memory:')
        try:
            connection.execute('CREATE TABLE installed_bundle (KEY TEXT, VALUE TEXT)')
            for key, user, token in [(BUNDLE, 100, 111), (BUNDLE + 'data', 100, 222),
                                     ('unrelated', 100, 333), (BUNDLE + '_1', 101, 444)]:
                connection.execute('INSERT INTO installed_bundle VALUES (?, ?)', (key,
                    json.dumps(dict(bundleUserInfo=dict(userId=user), accessTokenId=token))))
            result = API['bms_links'](connection)
        finally:
            connection.close()
        self.assertEqual(result['private_tokens'], {111})
        self.assertEqual(result['bundle_rows'], 2)

    def test_token_bundle_and_user_scope(self):
        connection = sqlite3.connect(':memory:')
        try:
            connection.execute('CREATE TABLE hap_token_info (bundle_name TEXT, user_id INTEGER, token_id INTEGER)')
            for row in [(BUNDLE, 100, 111), (BUNDLE, 101, 222), ('other', 100, 333)]:
                connection.execute('INSERT INTO hap_token_info VALUES (?, ?, ?)', row)
            result = API['token_links'](connection)
        finally:
            connection.close()
        self.assertEqual(result['private_tokens'], {111})
        self.assertEqual(result['user100_records'], 1)

    def test_match_does_not_export_tokens(self):
        bms = dict(bundle_rows=1, user100_records=1, private_tokens={123456789})
        token = dict(user100_records=1, private_tokens={123456789})
        result = API['summarize_links'](bms, token)
        self.assertTrue(result['unique_user100_token_matches'])
        self.assertNotIn('123456789', json.dumps(result))
        token['private_tokens'] = {987654321}
        self.assertFalse(API['summarize_links'](bms, token)['unique_user100_token_matches'])

    def test_missing_reference_is_not_a_match(self):
        bms = dict(bundle_rows=1, user100_records=1, private_tokens=set())
        token = dict(user100_records=0, private_tokens=set())
        self.assertFalse(API['summarize_links'](bms, token)['unique_user100_token_matches'])


if __name__ == '__main__':
    unittest.main()
