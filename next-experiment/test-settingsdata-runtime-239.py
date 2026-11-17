"""Synthetic parser checks only, not runtime observations."""
from pathlib import Path
import runpy
import unittest

events = runpy.run_path(str(Path(__file__).with_name('analyze-settingsdata-runtime-238.py')))['events']


class EventTests(unittest.TestCase):
    def test_provider_identity_is_required(self):
        text = ('SYNTHETIC ONLY\n'
                'other.bundle/APPSPAWN: DoAppSandboxMountOnce section app-base failed\n'
                'com.ohos.settingsdata/APPSPAWN: DoAppSandboxMountOnce section app-base failed\n')
        result = events(text)['provider_sandbox_base_failure']
        self.assertEqual(result, dict(count=1, first_line=3, last_line=3))

    def test_background_creation_is_not_main_ability(self):
        result = events('SYNTHETIC ONLY SettingsExtServiceAbility --> onCreate\n')
        self.assertEqual(result['settings_background_extension_created']['count'], 1)
        self.assertEqual(result['settings_launch_requests']['count'], 0)
        self.assertEqual(result['settings_main_ability_name_references']['count'], 0)

    def test_cli_error_is_not_bundle_absence(self):
        result = events('SYNTHETIC ONLY Error Code:10103601 specified bundleName does not exist\n')
        self.assertTrue(all(row['count'] == 0 for row in result.values()))


if __name__ == '__main__':
    unittest.main()
