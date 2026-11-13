"""Source contracts for observation-only 006; shell behavior is tested on ARM64."""
from pathlib import Path
import hashlib
import re
import runpy
import unittest

BASE = Path(__file__).resolve().parent


def parent_source():
    source = (BASE / 'baremetal-diagnostic-init.c').read_text()
    for name in ('storage-002', 'board-003', 'deadline-004', 'display-005'):
        source = runpy.run_path(str(BASE / ('baremetal-diagnostic-' + name + '.py')))['build_source'](source)
    return source


class Observation(unittest.TestCase):
    def candidate(self):
        path = BASE / 'baremetal-diagnostic-observation-006.py'
        self.assertTrue(path.exists(), 'Observation-only candidate is missing')
        return runpy.run_path(str(path))['build_source'](parent_source())

    def test_module_plan_and_existing_safety_gates_are_unchanged(self):
        before, after = parent_source(), self.candidate()
        pattern = r'const char \*modules\[\] = \{([^}]+)\}'
        self.assertEqual(re.search(pattern, before)[0], re.search(pattern, after)[0])
        for text in ('180, 30, requested', 'if (getpid() != 1)', 'diag_gate(1, kernel.release, command)',
                     'if (!budget_ready(timeout))', 'if (!budget_ready(15))'):
            self.assertIn(text, after)

    def test_observation_runs_before_final_binding_and_enumeration(self):
        source = self.candidate()
        wait = source.index('probe("drm-observation-window"')
        self.assertLess(source.index('probe("bindings-before-modules"'), wait)
        self.assertLess(wait, source.index('probe("bindings-after-modules"'))
        self.assertLess(wait, source.index('probe("enumeration"'))

    def test_dp_gpu_aux_and_ec_state_are_observed_without_writes(self):
        source = self.candidate()
        for text in ('ae90000.displayport-controller', 'ae98000.displayport-controller',
                     '3d00000.gpu', '3d6a000.gmu', '/sys/bus/auxiliary/devices/*',
                     '/sys/bus/platform/devices/*ucsi*'):
            self.assertIn(text, source)


if __name__ == '__main__':
    unittest.main()
