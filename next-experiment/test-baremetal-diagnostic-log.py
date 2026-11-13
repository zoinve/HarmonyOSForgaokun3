"""Exercise the actual static snapshot function on scratch files, never as PID1."""
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
CANDIDATE = next((name for name in ('--candidate-002', '--candidate-003', '--candidate-004') if name in sys.argv), None)
if CANDIDATE:
    sys.argv.remove(CANDIDATE)


class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='diagnostic-snapshot-')
        folder = Path(cls.temp.name)
        entry = BASE / 'baremetal-diagnostic-init.c'
        if CANDIDATE:
            generate = runpy.run_path(str(BASE / 'baremetal-diagnostic-storage-002.py'))['build_source']
            candidate = folder / 'candidate.c'
            contents = generate(entry.read_text())
            if CANDIDATE in ('--candidate-003', '--candidate-004'):
                contents = runpy.run_path(str(BASE / 'baremetal-diagnostic-board-003.py'))['build_source'](contents)
            if CANDIDATE == '--candidate-004':
                contents = runpy.run_path(str(BASE / 'baremetal-diagnostic-deadline-004.py'))['build_source'](contents)
            candidate.write_text(contents)
            entry = candidate
        source = folder / 'snapshot-test.c'
        # Include the unchanged production translation unit so this calls its
        # real static snapshot(), not a separately copied implementation.
        source.write_text('''
#define main diagnostic_unused_entry
#include "baremetal-diagnostic-init.c"
#undef main
#include <signal.h>
#include <sys/resource.h>
int main(int argc, char **argv)
{
    if (argc != 4 || getpid() == 1) return 90;
    ram = open(argv[1], O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    run = open(argv[2], O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    if (ram < 0 || run < 0) return 91;
    if (!strcmp(argv[3], "limit")) {
        struct rlimit limit = {128, 128};
        if (signal(SIGXFSZ, SIG_IGN) == SIG_ERR || setrlimit(RLIMIT_FSIZE, &limit)) return 92;
    }
    snapshot();
    close(ram); close(run);
    return 0;
}
'''.replace('#include "baremetal-diagnostic-init.c"', '#include "' + str(entry) + '"'))
        cls.binary = folder / 'snapshot-test'
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(BASE),
                        str(source), str(BASE / 'baremetal-diagnostic-core.c'),
                        '-o', str(cls.binary)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def exercise(self, folder, mode='normal'):
        return subprocess.run([str(self.binary), str(folder / 'ram.log'), str(folder / 'out'), mode],
                              text=True, capture_output=True, timeout=5, check=True)

    def prepare(self, folder):
        (folder / 'out').mkdir()
        data = b'PHASE_BEGIN nvme\n' + bytes(range(256)) * 43 + b'PHASE_END nvme status=7\n'
        (folder / 'ram.log').write_bytes(data)
        return data

    def test_full_multichunk_copy_has_private_permissions_and_success_record(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name); data = self.prepare(folder)
            p = self.exercise(folder)
            log = folder / 'out/phase-001.log'
            self.assertEqual(log.read_bytes(), data)
            self.assertEqual(log.stat().st_mode & 0o777, 0o600)
            self.assertIn('failed=0', p.stderr)
            self.assertEqual((folder / 'ram.log').read_bytes(), data)

    def test_existing_snapshot_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name); self.prepare(folder)
            log = folder / 'out/phase-001.log'; log.write_bytes(b'completed evidence')
            p = self.exercise(folder)
            self.assertIn('SNAPSHOT_OPEN_FAILED', p.stderr)
            self.assertEqual(log.read_bytes(), b'completed evidence')

    def test_snapshot_symlink_is_refused_without_changing_target(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name); self.prepare(folder)
            target = folder / 'protected'; target.write_bytes(b'untouched')
            (folder / 'out/phase-001.log').symlink_to(target)
            p = self.exercise(folder)
            self.assertIn('SNAPSHOT_OPEN_FAILED', p.stderr)
            self.assertEqual(target.read_bytes(), b'untouched')

    def test_real_file_size_limit_records_failure_not_success(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name); data = self.prepare(folder)
            p = self.exercise(folder, 'limit')
            self.assertIn('failed=1', p.stderr)
            self.assertNotIn('failed=0', p.stderr)
            self.assertEqual((folder / 'out/phase-001.log').stat().st_size, 128)
            self.assertEqual((folder / 'ram.log').read_bytes(), data)


if __name__ == '__main__':
    unittest.main()
