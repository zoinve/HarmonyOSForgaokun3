"""Verify one real-command cycle and restoration paths before device boot."""
from pathlib import Path
import json
import runpy
import socket
import subprocess
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
MOCK = runpy.run_path(str(BASE/'test-commercial-stop-089.py'))['MOCK']
WPA = r'''
if cmd == 'ld-linux-aarch64.so.1':
    mode = args[-1]
    assert mode in ('status', 'disconnect', 'reconnect')
    if mode == 'status':
        print('wpa_state=' + state['wpa'])
        status = state.get('status_exit', 0)
    else:
        state['commands'].append(mode)
        status = state.get(mode + '_exit', 0)
        if mode == 'disconnect': state['wpa'] = 'DISCONNECTED'
        elif status == 0: state['wpa'] = 'COMPLETED'
        print('OK' if status == 0 else 'FAIL')
elif cmd == 'sleep':
'''
MOCK = MOCK.replace("if cmd == 'sleep':\n", WPA)


class RefreshFlow(unittest.TestCase):
    def run_case(self, **changes):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'bin').mkdir()
            (root/'data/local/tmp/wpa_ctrl').mkdir(parents=True)
            state = dict(now=100, scene='100', guide=True, stops=0, ready=True,
                         wpa='COMPLETED', commands=[])
            state.update(changes)
            (root/'state').write_text(json.dumps(state))
            (root/'uptime').write_text('100.00 0\n')
            (root/'attr').write_text('fixture_context\n')
            for cmd in ('sleep', 'pidof', 'timeout', 'cat', 'grep', 'id', 'ld-linux-aarch64.so.1'):
                path = root/'bin'/cmd
                path.write_text('#!' + sys.executable + '\n' + MOCK)
                path.chmod(0o755)
            script = (BASE/'commercial-network-refresh-090.sh').read_text()
            script = script.replace('/system/bin/', str(root/'bin') + '/')
            script = script.replace('/network083/lib/ld-linux-aarch64.so.1', str(root/'bin/ld-linux-aarch64.so.1'))
            script = script.replace('/data/', str(root/'data') + '/').replace('/proc/uptime', str(root/'uptime'))
            script = script.replace('/proc/self/attr/current', str(root/'attr'))
            with socket.socket(socket.AF_UNIX) as control:
                control.bind(str(root/'data/local/tmp/wpa_ctrl/wlan0'))
                result = subprocess.run(['sh', '-c', script], timeout=25)
            return (json.loads((root/'state').read_text()),
                    (root/'data/commercial-desktop086.log').read_text(), result.returncode)

    def test_one_cycle(self):
        state, log, status = self.run_case()
        self.assertEqual(state['commands'], ['disconnect', 'reconnect'])
        self.assertEqual(status, 0)
        self.assertEqual(state['wpa'], 'COMPLETED')
        self.assertIn('wpa_state=DISCONNECTED', log)
        self.assertIn('REFRESH090_END', log)

    def test_failed_disconnect_still_restores(self):
        state, log, status = self.run_case(disconnect_exit=1)
        self.assertEqual(state['commands'], ['disconnect', 'reconnect'])
        self.assertEqual(state['wpa'], 'COMPLETED')
        self.assertIn('REFRESH090_DISCONNECT_RESULT exit_status=1', log)

    def test_failed_reconnect_is_not_retried_or_claimed(self):
        state, log, status = self.run_case(reconnect_exit=1)
        self.assertEqual(state['commands'], ['disconnect', 'reconnect'])
        self.assertEqual(state['wpa'], 'DISCONNECTED')
        self.assertIn('REFRESH090_RECONNECT_RESULT exit_status=1', log)

    def test_no_association_no_cycle(self):
        state, log, status = self.run_case(wpa='SCANNING')
        self.assertEqual(state['commands'], [])
        self.assertEqual(status, 1)

    def test_failed_status_no_cycle(self):
        state, log, status = self.run_case(status_exit=1)
        self.assertEqual(state['commands'], [])
        self.assertIn('reason=association_not_completed', log)

    def test_changed_scene_no_cycle(self):
        state, log, status = self.run_case(change=True)
        self.assertEqual(state['commands'], [])
        self.assertIn('reason=scene_changed', log)

    def test_absent_guide_no_cycle(self):
        state, log, status = self.run_case(guide=False)
        self.assertEqual(state['commands'], [])
        self.assertIn('reason=guide_or_socket_absent', log)

    def test_multiple_scenes_no_cycle(self):
        state, log, status = self.run_case(scene='100 200')
        self.assertEqual(state['commands'], [])
        self.assertIn('reason=not_one_scene', log)


if __name__ == '__main__':
    unittest.main()
