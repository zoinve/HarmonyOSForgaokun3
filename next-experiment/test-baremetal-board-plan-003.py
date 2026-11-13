"""Source-contract regression only; not proof of hardware probe success."""
from pathlib import Path
import re
import runpy
import sys
import unittest

BASE = Path(__file__).resolve().parent
CANDIDATE = '--candidate-003' in sys.argv
if CANDIDATE:
    sys.argv.remove('--candidate-003')


class BoardPlan(unittest.TestCase):
    def test_explicit_running_board_suppliers_precede_consumers(self):
        source = (BASE / 'baremetal-diagnostic-init.c').read_text()
        storage = runpy.run_path(str(BASE / 'baremetal-diagnostic-storage-002.py'))['build_source']
        parent = storage(source)
        if CANDIDATE:
            source = runpy.run_path(str(BASE / 'baremetal-diagnostic-board-003.py'))['build_source'](parent)
        else:
            source = parent
        declaration = re.search(r'const char \*modules\[\] = \{([^}]+)\}', source)
        self.assertIsNotNone(declaration)
        modules = re.findall(r'"([a-z0-9_]+)"', declaration[1])
        for supplier, consumer in [('i2c_qcom_geni', 'huawei_gaokun_ec'),
                                   ('qcom_refgen_regulator', 'msm'),
                                   ('spi_geni_qcom', 'himax_hx83121a_spi')]:
            self.assertIn(supplier, modules, 'Missing explicit board supplier')
            self.assertIn(consumer, modules, 'Missing actual board driver')
            self.assertLess(modules.index(supplier), modules.index(consumer))
        self.assertNotIn('i2c_hid_of', modules)
        # The exact module declaration is the only change from the tested 002.
        self.assertEqual(source[:declaration.start()], parent[:declaration.start()])
        self.assertEqual(source[declaration.end():], parent[parent.index('};', declaration.start()) + 1:])


if __name__ == '__main__':
    unittest.main()
