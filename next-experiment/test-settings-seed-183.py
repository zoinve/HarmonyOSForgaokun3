'''Focused selection and ZIP-inspection tests, not signature acceptance.'''
import io
import json
from pathlib import Path
import runpy
import unittest
import zipfile

API = runpy.run_path(str(Path(__file__).with_name('audit-settings-seed-183.py')))


class Tests(unittest.TestCase):
    def test_named_settings(self):
        self.assertTrue(API['selected_hap']('./.hmos-app/Settings/Settings.hap'))
        self.assertTrue(API['selected_hap']('./.hmos-app/PCSettings/PCSettings.hap'))

    def test_bundle_entry(self):
        self.assertTrue(API['selected_hap']('./app/com.huawei.hmos.settings/entry.hap'))

    def test_exclude_non_hap_state(self):
        for path in ['./settings/token.json', './app/Camera/entry.hap', './settings.db']:
            self.assertFalse(API['selected_hap'](path))

    def test_no_signature_claim(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr('module.json', json.dumps(dict(app=dict(
                bundleName='com.huawei.hmos.settings', versionName='fixture'))))
        result = API['inspect_hap'](stream.getvalue())
        self.assertEqual(result['bundle_name'], 'com.huawei.hmos.settings')
        self.assertFalse(result['hap_sign_marker_in_tail'])
        self.assertFalse(result['cryptographic_signature_verified'])


if __name__ == '__main__':
    unittest.main()
