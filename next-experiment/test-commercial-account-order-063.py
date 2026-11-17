"""Offline flow tests, not target account or desktop success evidence."""
from pathlib import Path
import runpy
import subprocess
import unittest

B = Path(__file__).resolve().parent
module = runpy.run_path(str(B / 'commercial-account-order-063.py'))
original = runpy.run_path(str(B / 'test-commercial-desktop-order-020.py'))['original']


class Tests(unittest.TestCase):
    def run_flow(self, *, ready='false', stop=0, start=0, wms='true'):
        script = module['repair'](original)
        begin = script.index('(umask 077;')
        end = script.index("printf 'COMMERCIAL063_ACCOUNT_SCRIPT_BEGIN", begin)
        script = script[:begin] + script[end:]
        for old, new in [('/usr/bin/begetctl', 'fake_begetctl'),
                         ('/system/bin/pidof', 'fake_pidof'),
                         ('/system/bin/sleep', 'fake_sleep'), ('/usr/bin/aa', 'fake_aa')]:
            script = script.replace(old, new)
        stubs = '''read_param() {
 case "$1" in
 bootevent.account.ready) printf '%s' READY ;;
 bootevent.wms.ready) printf '%s' WMS ;;
 *) printf true ;;
 esac
}
fake_pidof() { return 0; }
fake_sleep() { :; }
fake_aa() { echo UNEXPECTED_AA; return 1; }
fake_begetctl() {
 echo INIT_REQUEST "$@"
 case "$1" in stop_service) return STOP_RESULT ;; start_service) return START_RESULT ;; esac
}
'''
        for key, value in [('READY', ready), ('WMS', wms), ('STOP_RESULT', stop), ('START_RESULT', start)]:
            stubs = stubs.replace(key, str(value))
        subprocess.run(['sh', '-n'], input=script, text=True, capture_output=True, check=True)
        return subprocess.run(['sh'], input=stubs + script, text=True, capture_output=True, timeout=5)

    def test_bounded_original_restart_without_inferred_success(self):
        p = self.run_flow()
        self.assertEqual(p.returncode, 1)
        self.assertEqual(p.stdout.count('INIT_REQUEST stop_service accountmgr'), 1)
        self.assertEqual(p.stdout.count('INIT_REQUEST start_service accountmgr'), 1)
        self.assertIn('ACCOUNT_READY_TIMEOUT checks=60', p.stdout)

    def test_ready_account_unchanged(self):
        p = self.run_flow(ready='true')
        self.assertEqual(p.returncode, 0)
        self.assertNotIn('INIT_REQUEST', p.stdout)

    def test_original_init_refusals_propagate(self):
        p = self.run_flow(stop=7)
        self.assertEqual(p.returncode, 7)
        self.assertNotIn('start_service accountmgr', p.stdout)
        self.assertEqual(self.run_flow(start=8).returncode, 8)

    def test_no_restart_before_wms(self):
        p = self.run_flow(wms='false')
        self.assertEqual(p.returncode, 1)
        self.assertNotIn('INIT_REQUEST', p.stdout)

    def test_no_permission_or_flag_workaround(self):
        script = module['repair'](original)
        for forbidden in ['acm switch', 'param set', 'setuid', 'setgid', 'LD_PRELOAD', 'force-stop']:
            self.assertNotIn(forbidden, script)
        self.assertIn('"$attempt" -lt 6', script)
        baseline = runpy.run_path(str(B / 'build-commercial-native-062.py'))['outer']
        patched = module['instrument_outer'](baseline)
        self.assertIn('/proc/%d/root' + module['LOG'], patched)
        self.assertIn('commercial_outer_stream044(path,16384);', patched)


if __name__ == '__main__':
    unittest.main()
