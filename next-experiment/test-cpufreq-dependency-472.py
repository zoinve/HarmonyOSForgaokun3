"""Check the bounded dependency insertion without loading a host module."""
from pathlib import Path
import runpy
import unittest

FIX = runpy.run_path(str(Path(__file__).with_name('build-cpufreq-native-471.py')))


class DependencyTest(unittest.TestCase):
    def test_load_before_board_modules(self):
        original = 'prefix\n            const char *modules[] = {"i2c_qcom_geni", "msm"};\nsuffix'
        result = FIX['dependency471'](original)
        self.assertLess(result.index('insmod'), result.index('const char *modules[]'))
        self.assertIn('/cpufreq471/icc-osm-l3.ko', result)
        self.assertIn('i -lt 20', result)
        self.assertIn('NOT_TASK_MANAGER_ACCEPTANCE', result)
        self.assertTrue(result.endswith('"msm"};\nsuffix'))
        self.assertNotIn('chmod', result)
        self.assertNotIn('scaling_setspeed', result)

    def test_reject_changed_or_duplicate_anchor(self):
        for source in ('unknown', '            const char *modules[] = {"i2c_qcom_geni",' * 2):
            with self.assertRaises(AssertionError):
                FIX['dependency471'](source)


if __name__ == '__main__':
    unittest.main()
