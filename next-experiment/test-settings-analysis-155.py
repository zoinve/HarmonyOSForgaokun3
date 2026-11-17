"""Keep Settings UI diagnosis separate from provider and unrelated errors."""
from pathlib import Path
import runpy
import unittest

summarize = runpy.run_path(str(Path(__file__).with_name('analyze-settings-155.py')))['summarize']


class SettingsAnalysis(unittest.TestCase):
    def test_provider_errors_are_not_ui_launches(self):
        row = summarize('01-01 08:00:29.0 123 124 E datashare ConnectDataShareExtAbility com.ohos.settingsdata.DataAbility ret=-1')
        self.assertEqual(row['settings_launches'], [])
        self.assertEqual(row['settings_install_failures'], [])

    def test_correlated_launch_and_error(self):
        lines = [
            '11-16 12:41:26.406 10050 13247 I AMS StartAbility ability:com.huawei.hmos.settings/com.huawei.hmos.settings.MainAbility',
            '11-16 12:41:26.407 1210 4540 W BMS [abcdef 123 0]bundle not exist -n com.huawei.hmos.settings -u 100 -i 0',
            '11-16 12:41:26.408 1210 4540 E AMS [abcdef 123 0]generate ability request local error:2097152',
        ]
        self.assertEqual(summarize('\n'.join(lines))['correlated_missing_bundle_launch_count'], 1)
        lines[-1] = lines[-1].replace('abcdef', 'aaaaaa')
        self.assertEqual(summarize('\n'.join(lines))['correlated_missing_bundle_launch_count'], 0)

    def test_install_context_matches_worker(self):
        lines = [
            '01-01 08:00:37.843 1210 3163 E HapVerify No HAP Signing Block before ZIP Central Directory',
            '01-01 08:00:37.843 1210 3163 E BMS hap file verify failed, bundlePath: /system/app/Settings/Settings.hap',
            '01-01 08:00:37.843 1210 3163 E BMS hap files check signature info failed 8519742',
        ]
        failure = summarize('\n'.join(lines))['settings_install_failures'][0]
        self.assertTrue(failure['signing_block_missing'])
        self.assertTrue(failure['signature_error_8519742'])
        lines[0] = lines[0].replace('3163', '9999')
        self.assertFalse(summarize('\n'.join(lines))['settings_install_failures'][0]['signing_block_missing'])


if __name__ == '__main__':
    unittest.main()
