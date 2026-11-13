"""Read-only independent allocator evidence, file preservation and Ubuntu state audit."""
from pathlib import Path

source=Path(__file__).with_name('verify-baremetal-freedreno-fence-002.py').read_text()
source=source.replace('baremetal-freedreno-fence-run-002','baremetal-buffer-vdi-run-004').replace('baremetal-freedreno-fence-package-002','baremetal-buffer-vdi-package-004')
start=source.index('prior=json.loads(');end=source.index('\n',start)
source=source[:start]+source[end+1:]
start=source.index('old={row');end=source.index('with tarfile.open',start)
source=source[:start]+"new={row['path']:row for row in package['files']}\nassert len(new)==34 and package['reference_files_unchanged']\nassert package['original_sdk_handle_sha256']=='9c3ab7c3c83e074d0238814153752656c28b56202f833ad07f34b2cffd640912'\n"+source[end:]
start=source.index('for marker in [');end=source.index("policy={'LoadState'",start)
source=source[:start]+'''assert run['original_sdk_handle_abi_verified'] and run['cpu_gpu_coherency_verified']
for marker in ['NATIVE_ALLOC004_HANDLE_ABI original_sdk=1 header_bytes=56 reserve_offset=48 reserve_fds=2 reserve_ints=3',
               'NATIVE_ALLOC004_RENDERER FD690', 'size=13x7 stride=256', 'size=1600x2560 stride=6400',
               'NATIVE_ALLOC004_PASS allocator_import_pixels no_kms_changes=1 desktop_not_tested=1']:
    assert marker in run['run']['stdout'],marker
for sample in [0,1]:
    for marker in [f'NATIVE_ALLOC004_PIXEL sample={sample} rgba=64,128,191,255',
                   f'NATIVE_ALLOC004_GPU_TO_CPU sample={sample} rgba=191,64,128,255']:
        assert marker in run['run']['stdout'],marker
'''+source[end:]
start=source.index('    result.update(');end=source.index('\n    out.write_text',start)
source=source[:start]+'''    result.update(archive_sha256=package['archive_sha256'],all_34_archive_and_remote_files_verified=True,
        original_sdk_handle_abi_verified=True,cpu_gpu_coherency_with_glFinish_verified=True,
        live_sandbox_policy_verified=True,fd_identity_warning_absent=True,kernel_is_ubuntu=True,
        new_native_kernel_allocator_run_verified=False,desktop_verified=False)
'''+source[end:]
compile(source,'allocator004-independent-verifier','exec')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
