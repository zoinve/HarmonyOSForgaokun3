"""Exercise the restricted reader, including command injection and log privacy."""
from pathlib import Path
import json
import os
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).with_name('live-debug-reader-156.c')


class Reader(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='live-reader156-')
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.binary = self.root / 'reader'
        compiled = subprocess.run(['cc', '-O2', '-Wall', '-Wextra', '-Werror',
            '-DDIAG_LOG_ROOT=' + json.dumps(str(self.root)), '-DDIAG_FOLLOW_SECONDS=1',
            str(SOURCE), '-o', str(self.binary)], capture_output=True)
        self.assertEqual(compiled.returncode, 0, compiled.stderr.decode())

    def invoke(self, command, arguments=None):
        env = dict(os.environ, SSH_ORIGINAL_COMMAND=command)
        return subprocess.run([str(self.binary), *(arguments or ['-c', 'read-only'])],
            env=env, capture_output=True, text=True, timeout=4)

    def test_rejects_shell_and_extra_arguments(self):
        for command in ['', 'sh', 'status; id', 'settings\nstatus', '$(id)', '../hilog', 'scp -t file']:
            self.assertEqual(self.invoke(command).returncode, 77, command)
        self.assertEqual(self.invoke('status', ['-c', 'read-only', 'extra']).returncode, 77)
        self.assertEqual(self.invoke('status', ['-c', 'id']).returncode, 77)

    def test_only_normalized_settings_events_leave_reader(self):
        secret = 'PRIVATE_KEYBOARD_AND_USB_SERIAL_CONTENT'
        lines = [secret,
            'StartAbility ability:com.huawei.hmos.settings/com.huawei.hmos.settings.MainAbility ' + secret,
            'bundle not exist -n com.huawei.hmos.settings -u 100 -i 0 ' + secret,
            'hap file verify failed, bundlePath: /system/app/Settings/Settings.hap ' + secret,
            'ConnectDataShareExtAbility com.ohos.settingsdata.DataAbility ret=-1 ' + secret]
        (self.root / 'hilog').write_text('\n'.join(lines) + '\n')
        result = self.invoke('settings')
        self.assertEqual(result.returncode, 0)
        self.assertNotIn(secret, result.stdout + result.stderr)
        self.assertEqual([json.loads(line)['event'] for line in result.stdout.splitlines()],
            ['settings_launch_requested', 'settings_bundle_absent_user100',
             'settings_install_signature_rejected', 'settings_read_complete'])

    def test_symlinks_and_nonregular_logs_refused(self):
        (self.root / 'private').write_text('secret')
        (self.root / 'hilog').symlink_to(self.root / 'private')
        self.assertEqual(self.invoke('settings').returncode, 74)
        (self.root / 'hilog').unlink()
        os.mkfifo(self.root / 'hilog')
        self.assertEqual(self.invoke('settings').returncode, 74)

    def test_live_follow_skips_history_and_sees_append(self):
        path = self.root / 'hilog'
        path.write_text('bundle not exist -n com.huawei.hmos.settings -u 100 old\n')
        proc = subprocess.Popen([str(self.binary), '-c', 'read-only'],
            env=dict(os.environ, SSH_ORIGINAL_COMMAND='follow-settings'),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: proc.poll() is None and proc.kill())
        self.assertEqual(json.loads(proc.stdout.readline())['event'], 'following_settings')
        with path.open('a') as stream:
            stream.write('StartAbility ability:com.huawei.hmos.settings/new\n')
        output, error = proc.communicate(timeout=4)
        self.assertEqual(proc.returncode, 0, error)
        self.assertEqual([json.loads(line)['event'] for line in output.splitlines()],
            ['settings_launch_requested', 'settings_read_complete'])

    def test_oversize_and_binary_lines_are_not_parsed(self):
        trigger = 'StartAbility ability:com.huawei.hmos.settings/new'
        (self.root / 'hilog').write_bytes((trigger + 'a' * 9000 + '\n' + trigger + '\0\n').encode())
        result = self.invoke('settings')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), '{"event":"settings_read_complete"}')


if __name__ == '__main__':
    unittest.main()
