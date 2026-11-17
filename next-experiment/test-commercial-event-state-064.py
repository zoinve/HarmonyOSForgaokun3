"""Exercise read-only diagnostics without real services, identities or parameters."""
from pathlib import Path
import json
import runpy
import subprocess
import unittest

B = Path(__file__).resolve().parent
module = runpy.run_path(str(B / 'commercial-event-state-064.py'))
original = runpy.run_path(str(B / 'test-commercial-desktop-order-020.py'))['original']


class Tests(unittest.TestCase):
    def test_declared_keys_complete(self):
        audit = json.loads((B.parent / 'reports/commercial-event-declarations-063-r2/result.json').read_text())
        declared = set()
        for service in audit['declared_service_events']:
            values = service['bootevents']
            declared.update([values] if isinstance(values, str) else values)
        self.assertTrue(declared.issubset(module['KEYS']))
        self.assertEqual(len(module['KEYS']), len(set(module['KEYS'])))

    def test_original_flow_preserved(self):
        before = runpy.run_path(str(B / 'commercial-account-order-063.py'))['repair'](original)
        after = module['repair'](original)
        self.assertEqual(after.replace(module['diagnostics'](), '', 1), before)
        subprocess.run(['sh', '-n'], input=after, text=True, capture_output=True, check=True)
        self.assertIn('set -C', after)
        for forbidden in ['param set', 'param save', 'force-stop', 'setuid', 'setgid', 'LD_PRELOAD', 'chmod', 'chown']:
            self.assertNotIn(forbidden, after)

    def test_diagnostics_bounded_and_failure_retained(self):
        script = module['diagnostics']()
        script = script.replace('    exec > ' + module['LOG'] + ' 2>&1 || exit 1\n', '')
        for name in ['id', 'ls', 'cat', 'sleep', 'param']:
            script = script.replace('/system/bin/' + name, 'fake_' + name)
        stubs = '''fake_id() { echo ID_OBSERVED "$@"; }
fake_ls() { echo FILE_OBSERVED "$@"; }
fake_cat() { echo FILE_READ "$@"; }
fake_sleep() { echo SLEEP "$@"; }
fake_param() { echo PARAM_REQUEST "$@"; return 7; }
'''
        p = subprocess.run(['sh'], input=stubs + script, text=True, capture_output=True, timeout=5)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdout.count('COMMERCIAL064_SNAPSHOT_BEGIN'), 5)
        self.assertEqual(p.stdout.count('SLEEP 15'), 4)
        self.assertEqual(p.stdout.count('COMMERCIAL064_VALUE_END result=7'), 5 * len(module['KEYS']))
        self.assertEqual(p.stdout.count('COMMERCIAL064_ACL_END result=7'), len(module['KEYS']))
        self.assertIn('COMMERCIAL064_EVENT_DIAGNOSTICS_END', p.stdout)

    def test_original_account_mock_tests(self):
        subprocess.run(['python3', str(B / 'test-commercial-account-order-063.py')], check=True)


if __name__ == '__main__':
    unittest.main()
