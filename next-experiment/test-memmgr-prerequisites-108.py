"""Test the actual C scaffold helper in an isolated temporary filesystem."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class PrerequisiteTests(unittest.TestCase):
    def scenario(self, setup=None):
        with tempfile.TemporaryDirectory(prefix='memmgr108-test-') as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            (root / 'dev').mkdir()
            if setup:
                setup(root)
            harness = root / 'harness.c'
            harness.write_text('''#include <stdlib.h>
static void fail(const char *message) { (void)message; exit(42); }
#include "commercial-memmgr-prerequisites-108.h"
int main(void) { commercial_memmgr108(); return 0; }
''')
            executable = root / 'harness'
            subprocess.run(['gcc', '-D_GNU_SOURCE', '-Wall', '-Wextra', '-Werror',
                '-DMEMMGR108_ROOT=' + '"' + str(root) + '"', '-I', str(BASE), str(harness), '-o', str(executable)], check=True, capture_output=True)
            run = subprocess.run([str(executable)], capture_output=True, timeout=5)
            log = root / 'data/commercial-memmgr108.log'
            source = root / 'data/local/tmp/memmgr-nohyperhold-v1/memcg'
            metadata = (source.lstat().st_mode & 0o7777) if source.exists() else None
            files = sorted(path.name for path in source.iterdir()) if source.is_dir() else None
            return run.returncode, log.read_text() if log.exists() else '', metadata, files

    def test_creates_only_empty_directories(self):
        status, log, mode, files = self.scenario()
        self.assertEqual(status, 0)
        self.assertEqual(log.count('created=1'), 5)
        self.assertIn('service_success_not_inferred=1', log)
        self.assertEqual(files, [])

    def test_existing_directory_metadata_preserved(self):
        def setup(root):
            path = root / 'data/local/tmp/memmgr-nohyperhold-v1/memcg'
            path.mkdir(parents=True)
            path.chmod(0o710)
            (path / 'existing').write_text('untouched')
        status, log, mode, files = self.scenario(setup)
        self.assertEqual(status, 0)
        self.assertEqual(mode, 0o710)
        self.assertEqual(files, ['existing'])

    def test_symlink_component_refused(self):
        def setup(root):
            (root / 'elsewhere').mkdir()
            (root / 'data/local').symlink_to(root / 'elsewhere')
        status, log, mode, files = self.scenario(setup)
        self.assertEqual(status, 42)
        self.assertIn('reason=not_directory', log)

    def test_regular_file_refused(self):
        status, log, mode, files = self.scenario(lambda root: (root / 'data/local').write_text('retain'))
        self.assertEqual(status, 42)
        self.assertIn('reason=not_directory', log)

    def test_prior_log_not_overwritten(self):
        status, log, mode, files = self.scenario(lambda root: (root / 'data/commercial-memmgr108.log').write_text('prior evidence'))
        self.assertEqual(status, 42)
        self.assertEqual(log, 'prior evidence')

    def test_log_symlink_refused(self):
        def setup(root):
            target = root / 'other'
            target.write_text('prior evidence')
            (root / 'data/commercial-memmgr108.log').symlink_to(target)
        status, log, mode, files = self.scenario(setup)
        self.assertEqual(status, 42)
        self.assertEqual(log, 'prior evidence')


if __name__ == '__main__':
    unittest.main()
