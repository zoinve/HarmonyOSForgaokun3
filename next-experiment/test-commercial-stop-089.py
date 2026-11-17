"""Exercise actual diagnostic shell control flow with isolated command fixtures."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
MOCK = r'''
import json, os, subprocess, sys
from pathlib import Path
p = Path(__file__).resolve().parent.parent
state = json.loads((p/'state').read_text())
cmd = Path(sys.argv[0]).name
args = sys.argv[1:]
status = 0
if cmd == 'sleep':
    state['now'] += int(args[0])
    if state.get('change') and int(args[0]) == 10:
        state['scene'] = '200'
        state['change'] = False
    (p/'uptime').write_text(str(state['now']) + '.00 0\n')
elif cmd == 'pidof':
    value = state['scene'] if args[0] == 'com.ohos.sceneboard' else ('300' if state['guide'] else '')
    if value: print(value)
    else: status = 1
elif cmd == 'hilog':
    if state['ready']: print('ResidentLayoutCacheMgr: getResidentList send EVENT_SMARTDOCK_INIT_FINISHED')
elif cmd == 'aa':
    assert args == ['force-stop', 'com.huawei.hmos.hwstartupguide']
    state['stops'] += 1
    status = state.get('aa_status', 0)
    if status == 0: state['guide'] = False
elif cmd == 'uitest': status = 1
elif cmd == 'timeout':
    sys.exit(subprocess.run(args[1:]).returncode)
elif cmd == 'cat':
    for name in args: sys.stdout.write(Path(name).read_text())
elif cmd == 'grep':
    status = 0 if args[-2] in Path(args[-1]).read_text() else 1
elif cmd == 'id': print('fixture identity')
else: raise AssertionError(cmd)
(p/'state').write_text(json.dumps(state))
sys.exit(status)
'''


class StopFlow(unittest.TestCase):
    def run_case(self, **changes):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'bin').mkdir()
            (root/'data').mkdir()
            state = dict(now=65, scene='100', guide=True, stops=0, ready=True)
            state.update(changes)
            (root/'state').write_text(json.dumps(state))
            (root/'uptime').write_text('65.00 0\n')
            (root/'attr').write_text('fixture_context\n')
            for cmd in ('sleep', 'pidof', 'hilog', 'aa', 'uitest', 'timeout', 'cat', 'grep', 'id'):
                path = root/'bin'/cmd
                path.write_text('#!' + sys.executable + '\n' + MOCK)
                path.chmod(0o755)
            script = (BASE/'commercial-desktop-089.sh').read_text().replace('/system/bin/', str(root/'bin') + '/')
            script = script.replace('/data/', str(root/'data') + '/').replace('/proc/uptime', str(root/'uptime'))
            script = script.replace('/proc/self/attr/current', str(root/'attr'))
            subprocess.run(['sh', '-c', script], check=True, timeout=25)
            return json.loads((root/'state').read_text()), (root/'data/commercial-desktop086.log').read_text()

    def test_one_successful_stop(self):
        state, log = self.run_case()
        self.assertEqual(state['stops'], 1)
        self.assertFalse(state['guide'])
        self.assertIn('DESKTOP089_STOP_RESULT exit_status=0', log)
        self.assertIn('DESKTOP089_SAMPLE target=130', log)

    def test_missing_marker_never_stops(self):
        state, log = self.run_case(ready=False)
        self.assertEqual(state['stops'], 0)
        self.assertIn('DESKTOP089_DOCK_TIMEOUT', log)

    def test_multiple_scenes_never_stop(self):
        state, log = self.run_case(scene='100 200')
        self.assertEqual(state['stops'], 0)
        self.assertIn('DESKTOP089_DOCK_TIMEOUT', log)

    def test_absent_guide_never_stops(self):
        state, log = self.run_case(guide=False)
        self.assertEqual(state['stops'], 0)
        self.assertIn('DESKTOP089_GUIDE_ABSENT', log)

    def test_changed_pid_rechecks_before_stop(self):
        state, log = self.run_case(change=True)
        self.assertEqual(state['stops'], 1)
        self.assertIn('DESKTOP089_SCENE_CHANGED', log)
        self.assertIn('DESKTOP089_DOCK_READY scene_pid=200', log)

    def test_failed_stop_not_retried(self):
        state, log = self.run_case(aa_status=1)
        self.assertEqual(state['stops'], 1)
        self.assertTrue(state['guide'])
        self.assertIn('DESKTOP089_STOP_RESULT exit_status=1', log)


if __name__ == '__main__':
    unittest.main()
