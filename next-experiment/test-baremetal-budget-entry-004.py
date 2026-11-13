"""Call actual generated probe() outside PID1 using real scratch subprocesses."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class EntryBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='diag-budget-entry-')
        cls.addClassCleanup(cls.temp.cleanup)
        folder = Path(cls.temp.name)
        generator = BASE / 'baremetal-diagnostic-deadline-004.py'
        if not generator.is_file():
            raise AssertionError('Missing deadline integration generator')
        source = (BASE / 'baremetal-diagnostic-init.c').read_text()
        for name in ('storage-002', 'board-003', 'deadline-004'):
            source = runpy.run_path(str(BASE / ('baremetal-diagnostic-' + name + '.py')))['build_source'](source)
        (folder / 'entry.c').write_text(source)
        (folder / 'harness.c').write_text(r'''
#define main unused_diagnostic_main
#include "entry.c"
#undef main
int main(int argc, char **argv) {
    if (argc != 3 || getpid() == 1) return 90;
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now)) return 91;
    budget_start = now.tv_sec + now.tv_nsec / 1e9;
    if (!strcmp(argv[1], "expired")) budget_start -= 160;
    if (!strcmp(argv[1], "invalid")) budget_start = -1;
    char *command[] = {"/bin/sh", "-c", "printf ran > \"$1\"; exit 7", "probe", argv[2], NULL};
    return probe("scratch-only", command, 15);
}
''')
        cls.binary = folder / 'harness'
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(BASE),
                        str(folder / 'harness.c'), str(BASE / 'baremetal-diagnostic-core.c'),
                        '-o', str(cls.binary)], check=True)

    def invoke(self, mode):
        with tempfile.TemporaryDirectory(prefix='diag-side-effect-') as directory:
            target = Path(directory) / 'marker with spaces'
            result = subprocess.run([str(self.binary), mode, str(target)],
                                    capture_output=True, text=True, timeout=5)
            return result, target.read_text() if target.exists() else None

    def test_expired_budget_never_executes_new_subprocess(self):
        result, marker = self.invoke('expired')
        self.assertEqual(result.returncode, 124)
        self.assertIsNone(marker)
        self.assertIn('BUDGET_REFUSED', result.stdout)

    def test_invalid_start_never_executes_new_subprocess(self):
        result, marker = self.invoke('invalid')
        self.assertEqual(result.returncode, 124)
        self.assertIsNone(marker)

    def test_available_budget_runs_real_subprocess_and_preserves_failure(self):
        result, marker = self.invoke('available')
        self.assertEqual(result.returncode, 7)
        self.assertEqual(marker, 'ran')
        self.assertIn('status=7', result.stdout)


if __name__ == '__main__':
    unittest.main()
