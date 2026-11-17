"""Offline shell-flow tests; mocks cannot establish target activation success."""
from pathlib import Path
import runpy
import subprocess
import unittest

BASE = Path(__file__).resolve().parent
repair = runpy.run_path(str(BASE / 'commercial-desktop-order-062.py'))['repair']
original = runpy.run_path(str(BASE / 'test-commercial-desktop-order-020.py'))['original']


class Tests(unittest.TestCase):
    def execute(self, *, ready='false', wms_after=0, scene=0, acm=0, aa=0):
        script = repair(original)
        for old, new in [('/system/bin/pidof', 'fake_pidof'), ('/system/bin/sleep', 'fake_sleep'),
                         ('/usr/bin/aa', 'fake_aa'), ('/system/bin/acm', 'fake_acm'),
                         ('/dev/kmsg', '/dev/stdout')]:
            script = script.replace(old, new)
        stubs = '''set -u
ticks=0
read_param() {
    case "$1" in
        bootevent.account.ready) printf '%s' READY ;;
        bootevent.wms.ready) [ "$ticks" -ge WMS_AFTER ] && printf true || printf false ;;
        *) printf true ;;
    esac
}
fake_pidof() { return SCENE; }
fake_sleep() { ticks=$((ticks + 1)); }
fake_aa() { echo AA_CALLED; return AA_RESULT; }
fake_acm() { echo ACM_CALLED "$@"; return ACM_RESULT; }
'''
        for key, value in [('READY', ready), ('WMS_AFTER', wms_after), ('SCENE', scene),
                           ('AA_RESULT', aa), ('ACM_RESULT', acm)]:
            stubs = stubs.replace(key, str(value))
        subprocess.run(['sh', '-n'], input=script, text=True, check=True, capture_output=True)
        return subprocess.run(['sh'], input=stubs + script, text=True, capture_output=True, timeout=5)

    def test_existing_sceneboard_retries_once(self):
        p = self.execute()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotIn('AA_CALLED', p.stdout)
        self.assertEqual(p.stdout.count('ACM_CALLED switch -i 100'), 1)

    def test_ready_account_is_not_touched(self):
        p = self.execute(ready='true')
        self.assertEqual(p.returncode, 0)
        self.assertNotIn('ACM_CALLED', p.stdout)

    def test_delayed_wms_and_timeout(self):
        self.assertEqual(self.execute(wms_after=4).returncode, 0)
        p = self.execute(wms_after=91)
        self.assertEqual(p.returncode, 1)
        self.assertNotIn('ACM_CALLED', p.stdout)

    def test_original_cli_failure_is_propagated(self):
        p = self.execute(acm=7)
        self.assertEqual(p.returncode, 7)
        self.assertEqual(p.stdout.count('ACM_CALLED'), 1)

    def test_scene_start_failure_is_propagated(self):
        p = self.execute(scene=1, aa=9)
        self.assertEqual(p.returncode, 1)
        self.assertNotIn('ACM_CALLED', p.stdout)
        self.assertEqual(p.stdout.count('AA_CALLED'), 6)

    def test_no_fabrication_or_identity_change(self):
        script = repair(original)
        for forbidden in ['param set', 'setuid', 'setgid', 'LD_PRELOAD', 'force-stop', 'stop_service', 'start_service']:
            self.assertNotIn(forbidden, script)
        self.assertEqual(script.count('/system/bin/acm switch -i 100'), 1)
        self.assertIn('"$checks" -lt 90', script)
        self.assertIn('"$attempt" -lt 6', script)


if __name__ == '__main__':
    unittest.main()
