from pathlib import Path
import runpy
import unittest

summarize = runpy.run_path(str(Path(__file__).with_name('analyze-live-debug-157.py')))['summarize']


class Analysis(unittest.TestCase):
    def test_requires_matching_original_namespace_and_live_client(self):
        log = '\n'.join([
            'LIVE157_LOAD status=0 optional_sidecar=1 original_runtime_unchanged=1',
            'LIVE157_CONTEXT target=123 net_inode=456 separate_mount_pid_namespaces=1 readonly_logs=1 pid1=1 address=192.168.10.210 port=22257',
            'NETWORK084_TARGET_CONTEXT pid=123 net_inode=456 mnt_inode=789 pid_inode=321 root_verified=1 mode=network connectivity_not_inferred=1'])
        client = dict.fromkeys(['authenticated_native_candidate_connected','hilog_grew_during_connection',
            'live_follow_protocol_completed','arbitrary_shell_refused'],True)
        self.assertTrue(summarize(log,client)['authenticated_native_readonly_channel_verified'])
        self.assertFalse(summarize(log.replace('net_inode=456 mnt','net_inode=999 mnt'),client)['authenticated_native_readonly_channel_verified'])
        self.assertFalse(summarize(log,{**client,'hilog_grew_during_connection':False})['authenticated_native_readonly_channel_verified'])
        self.assertFalse(summarize('',client)['authenticated_native_readonly_channel_verified'])


if __name__ == '__main__':
    unittest.main()
