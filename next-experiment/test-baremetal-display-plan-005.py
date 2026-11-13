"""Source-contract tests, not proof of hardware binding or display readiness."""
from pathlib import Path
import re
import runpy
import sys
import unittest

BASE = Path(__file__).resolve().parent
CANDIDATE = '--candidate-005' in sys.argv
if CANDIDATE:
    sys.argv.remove('--candidate-005')


def parent_source():
    source = (BASE / 'baremetal-diagnostic-init.c').read_text()
    for version in ('storage-002', 'board-003', 'deadline-004'):
        source = runpy.run_path(str(BASE / ('baremetal-diagnostic-' + version + '.py')))['build_source'](source)
    return source


class DisplayPlan(unittest.TestCase):
    def source(self):
        source = parent_source()
        if CANDIDATE:
            source = runpy.run_path(str(BASE / 'baremetal-diagnostic-display-005.py'))['build_source'](source)
        return source

    def test_explicit_clock_and_dp_phy_suppliers_before_msm(self):
        modules = re.findall(r'"([a-z0-9_]+)"', re.search(
            r'const char \*modules\[\] = \{([^}]+)\}', self.source())[1])
        for name in ('dispcc_sc8280xp', 'gpucc_sc8280xp', 'phy_qcom_qmp_combo'):
            self.assertIn(name, modules, 'Missing audited modular supplier')
            self.assertLess(modules.index(name), modules.index('msm'))
        self.assertLess(modules.index('msm'), modules.index('himax_hx83121a_spi'))

    def test_bound_observation_is_separate_from_modprobe_exit(self):
        source = self.source()
        self.assertIn('DEVICE_BINDINGS', source)
        self.assertIn('waiting_for_supplier', source)
        self.assertIn('/proc/modules', source)
        self.assertIn('ae94000.dsi', source)
        self.assertIn('spi*/spi*.0', source)
        self.assertIn('probe("binding-state", bindings, 5)', source)
        # Keep budget policy, disk identity and finalization unchanged.
        parent = parent_source()
        for start, end in [('static int lab_storage(void)', 'int main(void)'),
                           ('static int probe(', 'static int identify('),
                           ('    char *dmesg[]', '    return 1;')]:
            self.assertEqual(source[source.index(start):source.index(end, source.index(start))],
                             parent[parent.index(start):parent.index(end, parent.index(start))])


if __name__ == '__main__':
    unittest.main()
