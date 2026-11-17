"""Regression for the actual commercial aa start rejection observed in 020."""
from pathlib import Path
import runpy, shlex, unittest

base=Path(__file__).resolve().parent
assert (base/'commercial-desktop-order-021.py').is_file(), 'missing commercial aa argv correction'
repair=runpy.run_path(str(base/'commercial-desktop-order-021.py'))['repair']
fixture=runpy.run_path(str(base/'test-commercial-desktop-order-020.py'))

class Tests(unittest.TestCase):
    def test_reference_argv_without_unsupported_user_option(self):
        new=repair(fixture['original'])
        command=next(line.strip().split(' > ',1)[0] for line in new.splitlines() if line.strip().startswith('/usr/bin/aa start '))
        self.assertEqual(shlex.split(command), ['/usr/bin/aa','start','-b','com.ohos.sceneboard','-a','com.ohos.sceneboard.MainAbility','-m','pc_sceneboard'])
        self.assertIn('user_selection=aa_default',new)
        self.assertNotIn('user_id=100',new)
        self.assertTrue(new.startswith(fixture['original'].split(fixture['wait'])[0]))
        for forbidden in ['force-stop','param set','setuid','setgid','sandbox-switch off']:
            self.assertNotIn(forbidden,new)
        with self.assertRaises(AssertionError):repair(new)

if __name__=='__main__':unittest.main()
