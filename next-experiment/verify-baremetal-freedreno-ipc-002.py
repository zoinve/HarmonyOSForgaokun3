"""Independently verify real exec-separated consumer evidence and unchanged Ubuntu state."""
from pathlib import Path

base=Path(__file__).resolve().parent
source=(base/'verify-baremetal-freedreno-fence-002.py').read_text()
source=source.replace("prior=json.loads((reports/'baremetal-freedreno-fence-package-001/package.json').read_text())\n",'')
start=source.index('old={row');end=source.index('with tarfile.open(archive)',start)
source=source[:start]+"new={row['path']:row for row in package['files']};assert len(new)==9\n"+source[end:]
start=source.index('for marker in [');end=source.index("policy={'LoadState'",start)
source=source[:start]+r'''import re
assert run['cross_process_gpu_execution_verified']
for marker in ['renderer=FD690','IPC002_SYNC_FILE poll=1 revents=0x1',
 'IPC002_REIMPORT wait=0x30f6 status=0x30f2',
 'IPC002_PIXELS center=255,0,0,255 corner=0,0,255,255',
 'IPC002_MAPPED center_8_8=255,0,0,255 corner_0_8=0,0,255,255',
 'IPC002_PASS cross_process_dmabuf_and_native_fence desktop_not_tested=1']:
    assert marker in run['run']['stdout'],marker
transfers=re.findall(r'IPC002_TRANSFER producer=(\d+) consumer=(\d+) exec_consumer=1 sender_transfer_fds_closed=1 consumer_imported_fd_closed=1',run['run']['stdout'])
assert len(transfers)==1 and transfers[0][0]!=transfers[0][1]
producer,consumer=map(int,transfers[0]);assert producer>1 and consumer>1
assert f'IPC002_CONSUMER pid={consumer} fence_poll=1 center=255,0,0,255 background=0,0,255,255 imported_fd_closed=1' in run['run']['stdout']
assert 'IPC002_FAIL' not in run['run']['stdout']+run['run']['stderr']
'''+source[end:]
start=source.index('    result.update(');end=source.index('    out.write_text',start)
source=source[:start]+'''    result.update(archive_sha256=package['archive_sha256'],all_nine_archive_and_remote_files_verified=True,
        producer_pid=producer,consumer_pid=consumer,distinct_exec_consumer_verified=True,
        sender_transfer_fds_closed=True,consumer_imported_fd_closed=True,
        consumer_received_native_fence_and_exact_gpu_pixels_verified=True,
        cross_process_gpu_execution_verified=True,live_sandbox_policy_verified=True,
        fd_identity_warning_absent=True,kernel_is_ubuntu=True,new_native_kernel_run_verified=False,
        initially_unsignaled_fence_verified=False,desktop_verified=False)
'''+source[end:]
source=source.replace('baremetal-freedreno-fence-package-002','baremetal-freedreno-ipc-package-002').replace('baremetal-freedreno-fence-run-002','baremetal-freedreno-ipc-run-002')
compile(source,'ipc002-independent-verification','exec')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
