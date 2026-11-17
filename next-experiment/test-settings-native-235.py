"""Check actual non-reaping wait semantics and narrow native source edits."""
from pathlib import Path
import os
import runpy
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
API = runpy.run_path(str(BASE / 'settings-native-235.py'))
PARENT = Path('/home/zoinve/harmony-virgl-883/commercial61-native-206/init.c')


class Native235Tests(unittest.TestCase):
    def test_source_scope(self):
        source = API['outer235'](PARENT.read_text())
        self.assertNotIn('settings206_start', source)
        self.assertNotIn('settings-launch-206.h', source)
        self.assertEqual(source.count('WNOWAIT'), 1)
        self.assertEqual(source.count('persistent172_pin(child);'), 3)
        sample = source.index('siginfo_t info235;')
        self.assertLess(source.index('persistent172_pin(child);'), sample)
        self.assertIn('elapsed033<720', source)
        self.assertIn('unsigned left033=900;', source)
        self.assertIn('persistent172_reaped(child,got);', source)
        self.assertIn('persistent172_finish();', source)
        self.assertIn('if (!failed) {\n        if (snapshot235_older[0]', source)

    def test_wait_observation_does_not_reap(self):
        child = os.fork()
        if child == 0:
            os._exit(69)
        try:
            observed = os.waitid(os.P_PID, child, os.WEXITED | os.WNOWAIT)
            self.assertEqual(observed.si_pid, child)
            self.assertEqual(observed.si_status, 69)
        finally:
            got, status = os.waitpid(child, 0)
        self.assertEqual(got, child)
        self.assertTrue(os.WIFEXITED(status))
        self.assertEqual(os.WEXITSTATUS(status), 69)

    def test_edited_snapshot_function_keeps_two_real_files(self):
        source = API['outer235'](PARENT.read_text())
        start = source.index('static void snapshot(void)')
        end = source.index('\nstatic int probe(', start)
        function = source[start:end]
        c = r'''#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include <dirent.h>
#include <string.h>
#include <stdlib.h>
static int ram=-1,run=-1;
static unsigned snapshot_id;
static char snapshot235_previous[40],snapshot235_older[40];
'''+function+r'''
int main(int argc,char **argv) {
 if(argc!=2)return 1;
 run=open(argv[1],O_RDONLY|O_DIRECTORY);if(run<0)return 2;
 ram=openat(run,"source",O_RDWR|O_CREAT|O_EXCL,0600);if(ram<0)return 3;
 for(unsigned i=0;i<6;++i){if(dprintf(ram,"iteration=%u\n",i)<0)return 4;snapshot();}
 if(faccessat(run,"phase-004.log",F_OK,0)==0)return 5;
 if(faccessat(run,"phase-005.log",F_OK,0)||faccessat(run,"phase-006.log",F_OK,0))return 6;
 return 0;
}
'''
        import subprocess
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'test.c').write_text(c)
            subprocess.run(['gcc', '-Wall', '-Wextra', '-Werror', str(root / 'test.c'), '-o', str(root / 'test')], check=True, capture_output=True)
            subprocess.run([str(root / 'test'), str(root)], check=True, capture_output=True)
            self.assertEqual(sorted(path.name for path in root.glob('phase-*.log')), ['phase-005.log', 'phase-006.log'])
            self.assertTrue((root / 'phase-006.log').read_bytes().startswith((root / 'phase-005.log').read_bytes()))


if __name__ == '__main__':
    unittest.main()
