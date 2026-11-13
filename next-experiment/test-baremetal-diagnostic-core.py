"""Real Linux tests for the diagnostic's safety boundary; no mounts/modules/reboot."""
import ctypes
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
SOURCE = BASE / 'baremetal-diagnostic-core.c'


class SafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert SOURCE.is_file(), 'Diagnostic safety implementation is missing'
        cls.temp = tempfile.TemporaryDirectory(prefix='diag-core-')
        library = Path(cls.temp.name) / 'core.so'
        subprocess.run(['gcc', '-shared', '-fPIC', '-O2', '-Wall', '-Wextra', '-Werror',
                        str(SOURCE), '-o', str(library)], check=True)
        cls.lib = ctypes.CDLL(str(library), use_errno=True)
        cls.lib.diag_gate.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
        cls.lib.diag_identity.argtypes = [ctypes.c_char_p]
        cls.lib.diag_new_run.argtypes = [ctypes.c_int, ctypes.c_char_p]
        cls.lib.diag_run.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.c_uint]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_gate_rejects_wrong_pid_release_and_nonexact_opt_in(self):
        release = b'7.1.0-rc3-gaokun3-el2'
        for pid, kernel, command in [(2, release, b'harmony.diag=1'),
                                     (1, release + b'+', b'harmony.diag=1'),
                                     (1, release, b''),
                                     (1, release, b'xharmony.diag=1'),
                                     (1, release, b'harmony.diag=10'),
                                     (1, release, b'harmony.diag=1 harmony.diag=0')]:
            with self.subTest(pid=pid, kernel=kernel, command=command):
                self.assertNotEqual(self.lib.diag_gate(pid, kernel, command), 0)
        self.assertEqual(self.lib.diag_gate(1, release, b'console=tty0 harmony.diag=1 quiet'), 0)

    def test_identity_requires_both_ids_and_ext4_without_duplicates(self):
        good = (b'UUID=00029cdd-1748-4d2f-b73b-8e8164922098\n'
                b'PART_ENTRY_UUID=24bd14b9-9d92-490a-ad15-a59c6b8e7cd9\nTYPE=ext4\n')
        self.assertEqual(self.lib.diag_identity(good), 0)
        for bad in [b'', good.replace(b'ext4', b'vfat'), good.replace(b'00029cdd', b'11129cdd'),
                    good.replace(b'24bd14b9', b'34bd14b9'), good + b'TYPE=ext4\n',
                    good.replace(b'PART_ENTRY_UUID=', b'OTHER=')]:
            self.assertNotEqual(self.lib.diag_identity(bad), 0)

    def test_exclusive_run_directory_rejects_reuse_symlink_and_traversal(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = os.open(folder, os.O_RDONLY | os.O_DIRECTORY)
            try:
                fd = self.lib.diag_new_run(parent, b'run-001')
                self.assertGreaterEqual(fd, 0)
                os.close(fd)
                self.assertEqual(self.lib.diag_new_run(parent, b'run-001'), -1)
                os.symlink('run-001', Path(folder) / 'link')
                for name in [b'link', b'../escape', b'.', b'', b'a/b']:
                    self.assertEqual(self.lib.diag_new_run(parent, name), -1)
            finally:
                os.close(parent)

    def test_command_reports_real_failure_and_bounded_timeout(self):
        def run(*args):
            argv = (ctypes.c_char_p * (len(args) + 1))(*[a.encode() for a in args], None)
            return self.lib.diag_run(argv, 1)
        self.assertEqual(run('/bin/sh', '-c', 'exit 7'), 7)
        self.assertEqual(run('/bin/sh', '-c', 'exit 0'), 0)
        self.assertEqual(run('/bin/sleep', '20'), 124)
        self.assertEqual(run('/does-not-exist'), 127)

    def test_real_entry_refuses_non_pid1_without_creating_files(self):
        entry = BASE / 'baremetal-diagnostic-init.c'
        self.assertTrue(entry.is_file(), 'Diagnostic PID1 is missing')
        binary = Path(self.temp.name) / 'diagnostic-init'
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', str(entry),
                        str(SOURCE), '-o', str(binary)], check=True)
        with tempfile.TemporaryDirectory() as folder:
            p = subprocess.run([str(binary)], cwd=folder, capture_output=True, text=True, timeout=3)
            self.assertEqual(p.returncode, 77)
            self.assertIn('requires PID 1', p.stderr)
            self.assertEqual(list(Path(folder).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
