"""Test timestamp parsing and query attribution before exporting the audit."""
from pathlib import Path
import runpy
import unittest

MODULE = runpy.run_path(str(Path(__file__).with_name('audit-devicedetect-server-102.py')))


class AuditTest(unittest.TestCase):
    def test_parse(self):
        row = MODULE['parse'](b'11-15 18:51:19.361   930  1455 I tag: hello')
        self.assertEqual(row['ms'], ((18*60+51)*60+19)*1000+361)
        self.assertEqual((row['pid'], row['tid'], row['body']), (930, 1455, b'I tag: hello'))
        self.assertIsNone(MODULE['parse'](b'01-01 08:00:19.361 930 1455 I early'))

    def test_attribution(self):
        markers = [b'ReadAbilityFilterList# abilityFilterList length:3',
                   b'stage = 1; res = 1; err = 0',
                   b'CheckDeviceAndReplySync# CheckDeviceAndReplySync deviceNum:0']
        rows = [dict(ms=t, pid=930, tid=1455, body=b, line=i)
                for i, (t, b) in enumerate(zip([100, 10824, 13129], markers), 1)]
        rows.append(dict(rows[0], pid=999, line=99))
        rows.append(dict(rows[0], tid=999, line=100))
        value = MODULE['analyze'](rows, 100, 14000)
        self.assertEqual(value['request_to_stage1_ms'], 10724)
        self.assertEqual(value['stage1_to_reply_ms'], 2305)
        self.assertEqual(len(value['evidence']), 3)

    def test_missing_or_ambiguous_evidence_rejected(self):
        with self.assertRaises(AssertionError):
            MODULE['analyze']([], 0, 10)
        row = dict(ms=1, pid=930, tid=1455, line=1,
                   body=b'ReadAbilityFilterList# abilityFilterList length:3')
        with self.assertRaises(AssertionError):
            MODULE['analyze']([row, row], 0, 10)


if __name__ == '__main__':
    unittest.main()
