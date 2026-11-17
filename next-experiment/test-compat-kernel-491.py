"""Check the exact kernel delta; no kernel/target operations in these tests."""
from pathlib import Path
import runpy
import unittest

BASE = Path(__file__).resolve().parent
API = runpy.run_path(str(BASE / 'build-compat-kernel-490.py'))


class ConfigTest(unittest.TestCase):
    def test_scoped_changes_preserve_binder_and_gpu(self):
        original = '''CONFIG_MEMCG=y
# CONFIG_MEMCG_V1 is not set
CONFIG_REBOOT_MODE=m
CONFIG_POWER_RESET_QCOM_PON=m
CONFIG_INTERCONNECT_QCOM_OSM_L3=m
CONFIG_ANDROID_BINDER_IPC=y
CONFIG_INPUT_PM8941_PWRKEY=y
CONFIG_DRM_MSM=m
CONFIG_LOCALVERSION="-gaokun3-el2"
'''
        fragment = (BASE / 'compat-kernel-489.config').read_text()
        result = API['expected_config'](original, fragment)
        self.assertEqual(result['CONFIG_MEMCG_V1'], 'y')
        self.assertEqual(result['CONFIG_POWER_RESET_QCOM_PON'], 'y')
        self.assertEqual(result['CONFIG_DRM_MSM'], 'm')
        self.assertEqual(result['CONFIG_LOCALVERSION'], '"-gaokun3-el2"')
        with self.assertRaises(AssertionError):
            API['expected_config'](original, fragment + '\nCONFIG_SECURITY_SELINUX=n\n')


if __name__ == '__main__':
    unittest.main()
