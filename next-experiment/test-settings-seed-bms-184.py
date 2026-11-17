import json
from pathlib import Path
import runpy
import unittest

API = runpy.run_path(str(Path(__file__).with_name('audit-settings-seed-bms-184.py')))


class Tests(unittest.TestCase):
    def test_path_scope(self):
        self.assertTrue(API['bms_path']('./.hmos-data/service/el1/public/bms/a.json'))
        self.assertFalse(API['bms_path']('./.hmos-data/service/el0/access_token/a.json'))

    def test_explicit_bundle(self):
        result = API['summarize_json'](json.dumps(dict(bundleName=API['BUNDLE'],
            versionName='fixture', token='PRIVATE_FIXTURE')).encode())
        self.assertEqual(result['settings_records'][0]['fields']['versionName'], 'fixture')
        self.assertNotIn('PRIVATE_FIXTURE', json.dumps(result))

    def test_bundle_key_and_unrelated(self):
        result = API['summarize_json'](json.dumps({API['BUNDLE']: dict(codePath='/system/app/Settings'),
            'other': dict(bundleName='other', versionName='not_settings')}).encode())
        self.assertEqual(len(result['settings_records']), 1)
        self.assertNotIn('not_settings', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
