"""Offline capture tests; no native boot, device access or fabricated GPU trace."""
from pathlib import Path
import runpy
import subprocess
import unittest

HERE = Path(__file__).parent


class CaptureTests(unittest.TestCase):
    def test_incremental_reader_retains_complete_lines_after_old_head_limit(self):
        self.assertTrue((HERE / 'native-perf-capture-045.h').exists(), 'missing incremental reader')
        code = r'''
#define _GNU_SOURCE
#include "native-perf-capture-045.h"
#include <assert.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    assert(argc == 2);
    int fd = open(argv[1], O_RDWR | O_CREAT | O_EXCL, 0600); assert(fd >= 0);
    char input[90000], output[65536];
    for (size_t k = 0; k < sizeof(input); ++k) input[k] = k % 100 == 99 ? '\n' : 'x';
    assert(write(fd, input, sizeof(input)) == sizeof(input));
    errno = EBUSY;
    struct capture045_result a = capture045_read(fd, 0, output, sizeof(output));
    assert(!a.error && a.complete == 65500 && a.partial == 36 && a.next == 65500 && errno == EBUSY);
    assert(!memcmp(input, output, a.complete));
    struct capture045_result b = capture045_read(fd, a.next, output, sizeof(output));
    assert(!b.error && b.complete == 24500 && b.next == 90000 && !b.partial);
    assert(!memcmp(input + a.next, output, b.complete));
    assert(write(fd, "part", 4) == 4);
    b = capture045_read(fd, 90000, output, sizeof(output));
    assert(!b.error && !b.complete && b.partial == 4 && b.next == 90000);
    assert(write(fd, "end\n", 4) == 4);
    b = capture045_read(fd, b.next, output, sizeof(output));
    assert(!b.error && b.complete == 8 && b.next == 90008 && !memcmp(output, "partend\n", 8));
    b = capture045_read(-1, 0, output, sizeof(output));
    assert(b.error == EBADF && b.read_bytes == -1 && !b.complete && !b.next && errno == EBUSY);
    b = capture045_read(fd, 0, output, 8);
    assert(b.error == EMSGSIZE && !b.complete && !b.next);
    close(fd);
}
'''
        script = '''from pathlib import Path
import tempfile, subprocess
with tempfile.TemporaryDirectory(prefix='native-capture045-unit-',dir='/home/zoinve/harmony-virgl-883') as d:
 p=Path(d); (p/'test.c').write_text(CODE)
 subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-I/mnt/d/lab/HarmonyOSForMatebookego/next-experiment',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test'),str(p/'input')],check=True)
'''
        r = subprocess.run(['wsl','-d','Debian','--','python3','-'],input='CODE='+repr(code)+'\n'+script,
                           text=True,capture_output=True,timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)

    def test_candidate_changes_only_read_only_capture_and_run_labels(self):
        p = HERE / 'build-native-original-graphics-boot-045.py'
        self.assertTrue(p.exists(), 'missing fresh capture candidate')
        ns = runpy.run_path(str(p))
        old = (HERE.parent / 'reports/native-original-graphics-boot-044/bootstrap.c').read_text()
        self.assertEqual(ns['restore_inner'](ns['inner']), old)
        self.assertIn('native_perf_capture045(sample);', ns['inner'])
        self.assertIn('2U * 1024U * 1024U', ns['inner'])
        self.assertIn('O_RDONLY|O_CLOEXEC|O_NOFOLLOW', ns['inner'])
        self.assertIn('MS_SLAVE', ns['inner'])
        self.assertNotIn('bootctl set-oneshot', ns['payload'])
        compile(ns['payload'], 'native045-build-offline', 'exec')

    def test_capacity_stop_never_fabricates_captured_bytes(self):
        ns = runpy.run_path(str(HERE / 'build-native-original-graphics-boot-045.py'))
        self.assertEqual(ns['HELPER'].count('total=limit'), 0,
                         'capacity exhaustion must not change the actual captured-byte counter')

    def test_independent_audit_preserves_original_images_and_prior_raw_evidence(self):
        path = HERE / 'verify-native-presentation-package-045.py'
        self.assertTrue(path.exists(), 'missing independent incremental-capture audit')
        p = runpy.run_path(str(path))['payload']
        self.assertIn('bootstrap_source_changes_only_incremental_perf_capture=True', p)
        self.assertIn('existing_native044_raw_files_verified=71', p)
        self.assertIn('original_images_independent_hashes=True', p)
        self.assertIn('native_boot_attempted=False', p)
        compile(p, 'native045-package-audit-offline', 'exec')


if __name__ == '__main__':
    unittest.main()
