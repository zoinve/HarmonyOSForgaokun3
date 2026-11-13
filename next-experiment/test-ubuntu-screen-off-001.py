"""Policy tests; D-Bus itself is separately checked on the actual Ubuntu host."""
from pathlib import Path
import runpy
import subprocess
import unittest


class ScreenOff(unittest.TestCase):
    def run_case(self, properties, current='i 0\n', set_status=0):
        path = Path(__file__).with_name('ubuntu-screen-off-001.py')
        self.assertTrue(path.exists(), 'Screen-off implementation is missing')
        commands = []

        def runner(args, **kwargs):
            commands.append(args)
            if args[:2] == ['loginctl', 'list-sessions']:
                text, code = 'c1 60578 gdm-greeter seat0 1 greeter tty1\n', 0
            elif args[:2] == ['loginctl', 'show-session']:
                # Actual loginctl silently returns no fields for a comma-joined filter.
                fields = {arg.removeprefix('--property=') for arg in args if arg.startswith('--property=')}
                text, code = (properties if fields == {'Name', 'User', 'Seat', 'Remote', 'Active', 'Type'} else ''), 0
            elif 'get-property' in args:
                changed = any('set-property' in c for c in commands)
                text, code = ('i 3\n' if changed and not set_status else current), 0
            else:
                self.assertIn('set-property', args)
                text, code = '', set_status
            return subprocess.CompletedProcess(args, code, text, 'denied' if code else '')

        result = runpy.run_path(str(path))['run_once'](runner)
        return result, commands

    def local(self, **changes):
        props = dict(Name='gdm-greeter', User='60578', Seat='seat0', Remote='no',
                     Active='yes', Type='wayland')
        props.update(changes)
        return ''.join(f'{k}={v}\n' for k, v in props.items())

    def test_local_graphical_session_is_turned_off_and_read_back(self):
        result, commands = self.run_case(self.local())
        self.assertEqual(result, [dict(session='c1', user='gdm-greeter', state='off', changed=True)])
        setters = [c for c in commands if 'set-property' in c]
        self.assertEqual(len(setters), 1)
        self.assertEqual(setters[0][-3:], ['PowerSaveMode', 'i', '3'])
        self.assertEqual(setters[0][:4], ['runuser', '-u', 'gdm-greeter', '--'])
        self.assertIn('--address=unix:path=/run/user/60578/bus', setters[0])

    def test_already_off_session_is_not_written_again(self):
        result, commands = self.run_case(self.local(), current='i 3\n')
        self.assertFalse(result[0]['changed'])
        self.assertFalse(any('set-property' in c for c in commands))

    def test_remote_inactive_and_text_sessions_are_untouched(self):
        for props in (self.local(Remote='yes'), self.local(Active='no'),
                      self.local(Type='tty'), self.local(Seat='')):
            with self.subTest(props=props):
                result, commands = self.run_case(props)
                self.assertEqual(result, [])
                self.assertFalse(any(c[0] == 'runuser' for c in commands))

    def test_dbus_failure_does_not_claim_off(self):
        result, _ = self.run_case(self.local(), set_status=1)
        self.assertEqual(result[0]['state'], 'error')


if __name__ == '__main__':
    unittest.main()
