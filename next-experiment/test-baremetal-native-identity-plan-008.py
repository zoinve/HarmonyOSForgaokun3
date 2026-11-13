"""Contract checks only; real helper ioctls are exercised separately in QEMU 009."""
from pathlib import Path
import re
import runpy
import unittest

BASE=Path(__file__).resolve().parent
def parent_source():
    source=(BASE/'baremetal-diagnostic-init.c').read_text()
    for version in ('storage-002','board-003','deadline-004','display-005','observation-006','ucsi-007'):
        source=runpy.run_path(str(BASE/('baremetal-diagnostic-'+version+'.py')))['build_source'](source)
    return source

class NativeIdentity(unittest.TestCase):
    def test_read_probe_does_not_change_module_plan_or_existing_guards(self):
        old=parent_source()
        new=runpy.run_path(str(BASE/'baremetal-diagnostic-native-identity-008.py'))['build_source'](old)
        self.assertEqual(re.search(r'const char \*modules\[\] = \{[^}]+\}',new)[0],re.search(r'const char \*modules\[\] = \{[^}]+\}',old)[0])
        for guard in ['getpid() != 1','diag_gate(1, kernel.release, command)','180, 30, requested','sleep(180)']:
            self.assertIn(guard,new)
        self.assertLess(new.index('probe("native-identity-read"'),new.index('const char *modules[]'))
        self.assertIn('probe("native-identity-read", identity_read, 8)',new)

if __name__=='__main__':unittest.main()
