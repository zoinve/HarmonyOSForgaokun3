from pathlib import Path
import runpy
import unittest

API = runpy.run_path(str(Path(__file__).with_name('classify-settings-deviceids-194.py')))


class Tests(unittest.TestCase):
    def test_unknown_values_not_exported_or_assumed_local(self):
        result = API['compare_literals'](['local', 'local', 'PRIVATE_DEVICE_FIXTURE'])
        self.assertEqual(result['known_literal_counts']['local'], 2)
        self.assertEqual(result['unclassified_value_count'], 1)
        self.assertNotIn('PRIVATE_DEVICE_FIXTURE', str(result))


if __name__ == '__main__':
    unittest.main()
