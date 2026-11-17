"""Exercise numeric-only radio observations alongside all original reader guards."""
from pathlib import Path
import json
import os
import runpy
import subprocess
import unittest

BASE=Path(__file__).resolve().parent
OLD=runpy.run_path(str(BASE/'test-live-debug-reader-156.py'))
SOURCE=runpy.run_path(str(BASE/'live-radio-reader-551.py'))['SOURCE']

class RadioReader(OLD['Reader']):
    def setUp(self):
        super().setUp()
        result=subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror',
            '-DDIAG_LOG_ROOT='+json.dumps(str(self.root)),'-DDIAG_FOLLOW_SECONDS=1',
            '-DDIAG_RADIO_MAXIMUM_READ=4096','-x','c','-','-o',str(self.binary)],
            input=SOURCE,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_radio_only_numeric_observations_leave_reader(self):
        private='PRIVATE_SSID_MAC_PASSPHRASE_NOT_FOR_EXPORT'
        lines=[private,'SHARE501_INTERFACE_ADD result=0 real_netdev_required=1',
            'SHARE501_SUPPLICANT_START result=0 group_connected_not_inferred=1',
            'SHARE501_PING pong=1 errno=0 transfer_verified=0',
            'SHARE501_PING pong=0 errno=2 transfer_verified=0',
            'SHARE501_PING pong=1 errno=0 transfer_verified=0 '+private]
        (self.root/'native').write_text('\n'.join(lines)+'\n')
        result=self.invoke('radio-status')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertNotIn(private,result.stdout+result.stderr)
        row=json.loads(result.stdout)
        self.assertEqual(row['interface_add_result'],0)
        self.assertEqual(row['supplicant_start_result'],0)
        self.assertEqual(row['ping_observations'],2)
        self.assertEqual((row['last_pong'],row['last_ping_errno']),(0,2))
        self.assertTrue(row['complete_snapshot_read'])
        self.assertTrue(row['current_connection_not_proven'])
        self.assertFalse(row['file_transfer_verified'])

    def test_radio_command_does_not_add_shell_or_argument_access(self):
        for command in ['radio-status; id','radio-status\nstatus','radio-status /etc/passwd']:
            self.assertEqual(self.invoke(command).returncode,77)
        self.assertEqual(self.invoke('radio-status',['-c','read-only','extra']).returncode,77)

    def test_radio_refuses_symlink_and_nonregular_logs(self):
        (self.root/'private').write_text('private')
        (self.root/'native').symlink_to(self.root/'private')
        self.assertEqual(self.invoke('radio-status').returncode,74)
        (self.root/'native').unlink()
        os.mkfifo(self.root/'native')
        self.assertEqual(self.invoke('radio-status').returncode,74)

    def test_radio_invalid_binary_and_overflow_records_are_ignored(self):
        lines=['SHARE501_PING pong=1 errno=2 transfer_verified=0',
               'SHARE501_PING pong=2 errno=0 transfer_verified=0',
               'SHARE501_PING pong=1 errno=0 transfer_verified=0\0',
               'SHARE501_PING pong=999999999999999999999999 errno=0 transfer_verified=0',
               'SHARE501_INTERFACE_ADD result=256 real_netdev_required=1']
        (self.root/'native').write_text('\n'.join(lines)+'\n')
        row=json.loads(self.invoke('radio-status').stdout)
        self.assertEqual(row['ping_observations'],0)
        self.assertEqual(row['interface_add_result'],-1)

    def test_radio_read_limit_does_not_claim_a_complete_or_current_result(self):
        path=self.root/'native'
        with path.open('wb') as stream:
            stream.write(b'SHARE501_INTERFACE_ADD result=0 real_netdev_required=1\n')
            stream.seek(4096)
            stream.write(b'SHARE501_PING pong=1 errno=0 transfer_verified=0\n')
        row=json.loads(self.invoke('radio-status').stdout)
        self.assertEqual(row['scanned_bytes'],4096)
        self.assertEqual(row['ping_observations'],0)
        self.assertFalse(row['complete_snapshot_read'])
        self.assertTrue(row['current_connection_not_proven'])

if __name__ == '__main__':
    unittest.main()
