"""Contract: 007 changes only the explicit UCSI request, preserving 006 observation."""
from pathlib import Path
import runpy
import unittest

BASE = Path(__file__).resolve().parent


def parent_source():
    source = (BASE / 'baremetal-diagnostic-init.c').read_text()
    for version in ('storage-002', 'board-003', 'deadline-004', 'display-005', 'observation-006'):
        source = runpy.run_path(str(BASE / ('baremetal-diagnostic-' + version + '.py')))['build_source'](source)
    return source


class UcsiPlan(unittest.TestCase):
    def test_only_ucsi_request_added_after_ec_before_display(self):
        p = BASE / 'baremetal-diagnostic-ucsi-007.py'
        self.assertTrue(p.exists(), 'UCSI-only follow-up is missing')
        before = parent_source()
        after = runpy.run_path(str(p))['build_source'](before)
        anchor = '"huawei_gaokun_ec", "ucsi_huawei_gaokun",'
        self.assertEqual(after.count(anchor), 1)
        self.assertEqual(after.replace('"ucsi_huawei_gaokun", ', '', 1), before)
        self.assertLess(after.index('"ucsi_huawei_gaokun"'), after.index('"msm"'))


if __name__ == '__main__':
    unittest.main()
