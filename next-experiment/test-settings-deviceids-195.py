from pathlib import Path
import runpy
import unittest

API = runpy.run_path(str(Path(__file__).with_name('decode-settings-deviceids-195.py')))


class Tests(unittest.TestCase):
    def test_json_vectors_not_misread_as_raw_device_ids(self):
        result = API['decode_counts'](['[\u00220\u0022]', '[0]', '[]', '[\u0022\u0022]'])
        self.assertEqual(result['json_zero_array'], 2)
        self.assertEqual(result['json_empty_array'], 1)
        self.assertEqual(result['json_empty_string_array'], 1)

    def test_unknown_and_boolean_not_treated_as_zero(self):
        result = API['decode_counts'](['[false]', 'false', '[\u0022PRIVATE_FIXTURE\u0022]', 'not-json'])
        self.assertEqual(result['json_other_array'], 2)
        self.assertEqual(result['json_other_value'], 1)
        self.assertEqual(result['non_json'], 1)
        self.assertNotIn('PRIVATE_FIXTURE', str(result))


if __name__ == '__main__':
    unittest.main()
