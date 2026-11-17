from pathlib import Path
import runpy
import unittest

summarize=runpy.run_path(str(Path(__file__).with_name('analyze-live-debug-161.py')))['summarize']


class StageAcceptance(unittest.TestCase):
    def test_failure_stage_does_not_become_live_acceptance(self):
        text='''LIVE159_LOAD status=0 optional_sidecar=1 original_runtime_unchanged=1
LIVE161_LOADER_READY source_hash_verified=1 ram_hash_verified=1 inherited_log_fds_present=1
LIVE161_STORAGE_REFUSED item=1 stage=6 errno=22
LIVE161_END status=93 namespace_reaped=1
LIVE159_STOP supervisor=3995 reaped=1 state=23808
'''
        result=summarize(text,{})
        self.assertEqual(result['storage_refusals'],[dict(item=1,stage=6,errno=22)])
        self.assertTrue(result['hash_checked_ram_loader_ready'])
        self.assertFalse(result['authenticated_native_readonly_channel_verified'])

    def test_inherited_init_and_new_helper_must_both_match(self):
        text='''LIVE159_LOAD status=0 optional_sidecar=1 original_runtime_unchanged=1
LIVE161_LOADER_READY source_hash_verified=1 ram_hash_verified=1 inherited_log_fds_present=1
LIVE161_STORAGE_READY item=1 readonly=1 source_regular=1
LIVE161_STORAGE_READY item=2 readonly=1 source_regular=1
LIVE161_STORAGE_READY item=3 key_copied_in_ram=1 key_material_not_reported=1
LIVE161_CONTEXT target=495 net_inode=4026533332 separate_mount_pid_namespaces=1 readonly_logs=1 pid1=1 address=192.168.10.142 port=22257 discovery_port=22259
NETWORK084_TARGET_CONTEXT pid=495 net_inode=4026533332 mnt_inode=100 pid_inode=101 root_verified=1 mode=network connectivity_not_inferred=1
LIVE161_END status=0 namespace_reaped=1
LIVE159_STOP supervisor=3995 reaped=1 state=0
'''
        client=dict(connected_address='192.168.10.142',authenticated_native_candidate_connected=True,
            discovered_endpoint_pinned_ssh_authenticated=True,hilog_grew_during_connection=True,
            live_follow_protocol_completed=True,arbitrary_shell_refused=True)
        self.assertTrue(summarize(text,client)['authenticated_native_readonly_channel_verified'])
        self.assertFalse(summarize(text.replace('source_hash_verified=1','source_hash_verified=0'),client)['authenticated_native_readonly_channel_verified'])
        self.assertFalse(summarize(text.replace('item=2 readonly=1','item=8 readonly=1'),client)['authenticated_native_readonly_channel_verified'])
        self.assertFalse(summarize(text,dict(client,connected_address='192.168.10.210'))['authenticated_native_readonly_channel_verified'])


if __name__ == '__main__':
    unittest.main()
