"""Offline source-plan gate; does not claim hardware driver initialization works."""
from pathlib import Path
import runpy
import sys
import unittest

BASE = Path(__file__).resolve().parent
MODE = sys.argv.pop(1) if len(sys.argv) > 1 else 'candidate'


class StoragePlanTests(unittest.TestCase):
    def test_pcie_supplier_is_probed_before_nvme_and_failure_stops_storage(self):
        parent = (BASE / 'baremetal-diagnostic-init.c').read_text()
        source = parent if MODE == 'baseline' else runpy.run_path(
            str(BASE / 'baremetal-diagnostic-storage-002.py'))['build_source'](parent)
        self.assertIn('    char *pcie_phy[]', source, 'Missing explicit PCIe PHY supplier phase')
        start = source.index('    char *pcie_phy[]')
        nvme = source.index('    char *nvme[]', start)
        self.assertIn('"phy_qcom_qmp_pcie"', source[start:nvme])
        self.assertIn('probe("pcie-phy", pcie_phy, 15)', source[start:nvme])
        self.assertIn('status ? status : probe("nvme", nvme, 15)', source[nvme:])
        self.assertLess(source.index('diag_gate(1,'), start)
        self.assertEqual(source.count('probe("pcie-phy", pcie_phy, 15)'), 1)


if __name__ == '__main__':
    unittest.main()
