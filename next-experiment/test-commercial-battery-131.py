"""Guard the battery-only outer-init change without touching hardware."""
from pathlib import Path
import ast
import runpy
import subprocess
import unittest

BASE = Path(__file__).resolve().parent
adapt = runpy.run_path(str(BASE / 'build-commercial-native-131.py'))['adapt']


class BatteryCandidateTests(unittest.TestCase):
    def test_module_order_and_read_only_probe(self):
        source = ('before "huawei_gaokun_ec", "ucsi_huawei_gaokun" after\n'
                  '            (void)probe("bindings-after-modules", bindings, 5);\ntail')
        result = adapt(source)
        self.assertIn('"huawei_gaokun_ec", "huawei_gaokun_battery", "ucsi_huawei_gaokun"', result)
        self.assertIn('GAOKUN_BATTERY131_END_NOT_HDI_ACCEPTANCE', result)
        self.assertIn(chr(92) + chr(34) + '$d' + chr(92) + chr(34), result)
        self.assertNotIn('@Q@', result)
        self.assertNotIn('CreateMock', result)
        self.assertNotIn('chmod', result)
        self.assertNotIn(' >', result)
        self.assertTrue(result.endswith('\ntail'))
        self.assertEqual(result.count('battery-real-sysfs-131'), 1)
        literals = []
        for line in result.splitlines():
            line = line.strip()
            if line.startswith(chr(34)):
                literals.append(ast.literal_eval(line.removesuffix(', NULL};')))
        command = ''.join(literals)
        self.assertIn('[ -d ' + chr(34) + '$d' + chr(34) + ' ]', command)
        subprocess.run(['sh', '-n'], input=command, text=True, check=True)

    def test_refuse_unknown_or_duplicate_source(self):
        for source in ('unknown', '"huawei_gaokun_ec", "ucsi_huawei_gaokun"' * 2):
            with self.assertRaises(AssertionError):
                adapt(source)


if __name__ == '__main__':
    unittest.main()
