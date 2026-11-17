"""Exercise the original recovery callback's boolean branch interpretation."""
from pathlib import Path
import json
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
audit = runpy.run_path(str(ROOT / 'next-experiment/audit-oobe-recovery-117.py'))
decoded = json.loads((ROOT / 'reports/sceneboard-oobe-audit-097/decoded-methods.json').read_bytes())
instructions = next(m['instructions'] for m in decoded['methods']
                    if 'BaseOobeManager&' in m['record'] and m['method']['name'] == '#~@0=@0*#')


class RecoveryBranches(unittest.TestCase):
    def test_active_reaches_trust_check(self):
        self.assertEqual(audit['predicate_destination'](instructions, 38, 50, True), 80)

    def test_inactive_reaches_finished_return(self):
        self.assertEqual(audit['predicate_destination'](instructions, 38, 50, False), 52)

    def test_trusted_reaches_restart(self):
        self.assertEqual(audit['predicate_destination'](instructions, 100, 112, True), 142)

    def test_untrusted_reaches_return(self):
        self.assertEqual(audit['predicate_destination'](instructions, 100, 112, False), 114)

    def test_unexpected_instruction_fails_closed(self):
        with self.assertRaises(AssertionError):
            audit['predicate_destination'](instructions, 27, 50, True)


if __name__ == '__main__':
    unittest.main()
