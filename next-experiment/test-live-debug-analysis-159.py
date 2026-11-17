from pathlib import Path
import runpy
import unittest

summarize = runpy.run_path(str(Path(__file__).with_name('analyze-live-debug-159.py')))['summarize']


class NativeAcceptance(unittest.TestCase):
    def test_requires_actual_endpoint_namespace_and_cleanup(self):
        text = '''LIVE159_LOAD status=0 optional_sidecar=1 original_runtime_unchanged=1
LIVE159_CONTEXT target=499 net_inode=4026533332 separate_mount_pid_namespaces=1 readonly_logs=1 pid1=1 address=192.168.10.142 port=22257 discovery_port=22259
NETWORK084_TARGET_CONTEXT pid=499 net_inode=4026533332 mnt_inode=100 pid_inode=101 root_verified=1 mode=network connectivity_not_inferred=1
LIVE159_END status=0 namespace_reaped=1
LIVE159_STOP supervisor=3978 reaped=1 state=0
'''
        client = dict(connected_address='192.168.10.142',authenticated_native_candidate_connected=True,
            discovered_endpoint_pinned_ssh_authenticated=True,hilog_grew_during_connection=True,
            live_follow_protocol_completed=True,arbitrary_shell_refused=True)
        self.assertTrue(summarize(text,client)['authenticated_native_readonly_channel_verified'])
        for field in ['authenticated_native_candidate_connected','discovered_endpoint_pinned_ssh_authenticated',
            'hilog_grew_during_connection','live_follow_protocol_completed','arbitrary_shell_refused']:
            self.assertFalse(summarize(text,dict(client,**{field:False}))['authenticated_native_readonly_channel_verified'])
        self.assertFalse(summarize(text,dict(client,connected_address='192.168.10.210'))['authenticated_native_readonly_channel_verified'])
        self.assertFalse(summarize(text.replace('pid=499 net_inode=4026533332','pid=499 net_inode=999'),client)['authenticated_native_readonly_channel_verified'])
        self.assertFalse(summarize(text.replace('namespace_reaped=1','namespace_reaped=0'),client)['authenticated_native_readonly_channel_verified'])
        self.assertFalse(summarize(text.replace('supervisor=3978 reaped=1','supervisor=3978 reaped=0'),client)['authenticated_native_readonly_channel_verified'])
        self.assertFalse(summarize('',client)['authenticated_native_readonly_channel_verified'])


if __name__ == '__main__':
    unittest.main()
