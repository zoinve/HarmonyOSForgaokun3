"""Real C budget decisions; no PID1, mounts, module loading or reboot."""
from pathlib import Path
import ctypes
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class BudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='diag-budget-')
        path = Path(cls.temp.name)
        cls.addClassCleanup(cls.temp.cleanup)
        header = BASE / 'baremetal-diagnostic-budget-004.h'
        if not header.is_file():
            raise AssertionError('Missing shared diagnostic budget implementation')
        (path / 'test.c').write_text('''
#include "baremetal-diagnostic-budget-004.h"
int allowance(double start, double now, unsigned requested) {
    return diag_budget_allow(start, now, 180, 30, requested);
}
''')
        subprocess.run(['gcc', '-shared', '-fPIC', '-O2', '-Wall', '-Wextra', '-Werror',
                        '-I', str(BASE), str(path / 'test.c'), '-o', str(path / 'test.so')], check=True)
        cls.library = ctypes.CDLL(str(path / 'test.so'))
        cls.allow = cls.library.allowance
        cls.allow.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_uint]
        cls.allow.restype = ctypes.c_int

    def test_requested_phase_must_fit_before_finalization_reserve(self):
        # Removing the reserve would incorrectly admit the last two requests.
        for start, now, request, expected in [(100, 100, 15, 1), (100, 235, 15, 1),
                                               (100, 235.001, 15, 0), (100, 249, 3, 0),
                                               (100, 250, 1, 0), (100, 281, 1, 0)]:
            with self.subTest(now=now, request=request):
                self.assertEqual(self.allow(start, now, request), expected)

    def test_each_request_uses_elapsed_time_not_a_fresh_budget(self):
        self.assertEqual([self.allow(0, t, 15) for t in (0, 120, 135, 140, 160)],
                         [1, 1, 1, 0, 0])

    def test_invalid_clock_and_empty_request_fail_closed(self):
        for start, now, request in [(-1, 0, 15), (100, 99, 15),
                                     (0, float('nan'), 15), (0, float('inf'), 15),
                                     (float('nan'), 10, 15), (0, 1, 0), (0, 0, 151)]:
            with self.subTest(start=start, now=now, request=request):
                self.assertEqual(self.allow(start, now, request), 0)


if __name__ == '__main__':
    unittest.main()
