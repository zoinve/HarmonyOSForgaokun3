"""Do not infer installation, exportability or valid signing from metadata hints."""
from pathlib import Path
import runpy
import unittest

API = runpy.run_path(str(Path(__file__).with_name('analyze-settings-routing-177.py')))


class RoutingTests(unittest.TestCase):
    def test_weak_runtime_hints_are_not_acceptance(self):
        pc = API['PC']
        row = API['observations']('Restore hap token 1 bundle name '+pc+' user 100, ok!\nkey:'+pc+'_-3 not found')
        self.assertEqual(row['token_restore_lines'], [1])
        self.assertEqual(row['special_user_key_miss_lines'], [2])
        self.assertFalse(row['user100_installation_verified'])
        self.assertFalse(row['ability_launch_verified'])

    def test_unrelated_bundle_is_excluded(self):
        row = API['observations']('Restore hap token 1 bundle name com.other user 100, ok!')
        self.assertEqual(row['token_restore_lines'], [])

    def test_missing_exported_stays_unknown(self):
        hap = dict(sha256='fixture', preceding_32_bytes_hex=b'<hap sign block>'.hex(),
            metadata={'module.json': dict(app=dict(bundleName='fixture'), module=dict(mainElement='Main',
                abilities=[dict(name='Main', visible=False, skills=[dict(actions=['action.settings.menu.v1'])])]))})
        row = API['routes'](hap)
        self.assertIsNone(row['abilities'][0]['exported'])
        self.assertTrue(row['preceding_bytes_contain_signature_marker'])
        self.assertFalse(row['cryptographic_verification_performed'])


if __name__ == '__main__':
    unittest.main()
