"""Own-buffer allocator coherency only, in the proven live-captured render-only sandbox."""
from pathlib import Path
import json
import runpy
import subprocess

base=Path(__file__).resolve().parent.parent
package=base/'reports/baremetal-buffer-vdi-package-004'
out=base/'reports/baremetal-buffer-vdi-run-004'
source=runpy.run_path(str(base/'next-experiment/run-baremetal-freedreno-fence-002.py'),run_name='payload_only')['source']
for old,new in [('harmony-lab-freedreno-fence-transfer-002','harmony-lab-buffer-vdi-transfer-004'),
                ('harmony-lab-freedreno-fence-sandbox-002','harmony-lab-buffer-vdi-sandbox-004'),
                ('harmony-lab-freedreno-fence-probe-002','harmony-lab-buffer-vdi-probe-004'),
                ('harmony-lab-freedreno-fence-002','harmony-lab-buffer-vdi-004'),
                ('FENCE001_PASS native_fence_and_dmabuf_coherence desktop_not_tested=1',
                 'NATIVE_ALLOC004_PASS allocator_import_pixels no_kms_changes=1 desktop_not_tested=1')]:
    assert old in source,old
    source=source.replace(old,new)
compile(source,'private-buffer-vdi004-remote','exec')
if __name__=='__main__':
    expected=json.loads((package/'package.json').read_text())
    assert expected['reference_files_unchanged'] and expected['all_needed_libraries_present']
    assert expected['original_sdk_handle_sha256']=='9c3ab7c3c83e074d0238814153752656c28b56202f833ad07f34b2cffd640912'
    assert len(expected['files'])==34
    assert not out.exists();out.mkdir()
    prepare="from pathlib import Path;p=Path('/home/zoinve/harmony-lab-buffer-vdi-transfer-004');assert not p.exists();p.mkdir(mode=0o700)"
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','python3 -'],input=prepare,text=True,capture_output=True,timeout=15)
    (out/'transfer-prepare.json').write_text(json.dumps(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2))
    r.check_returncode()
    subprocess.run(['scp',str(package/'bundle.tar.gz'),'matebook:/home/zoinve/harmony-lab-buffer-vdi-transfer-004/bundle.tar.gz'],check=True,timeout=90)
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],input='expected='+repr(expected)+'\n'+source,text=True,capture_output=True,timeout=170)
    (out/'remote.stdout').write_text(r.stdout,encoding='utf-8');(out/'remote.stderr').write_text(r.stderr,encoding='utf-8')
    r.check_returncode();report=json.loads(r.stdout)
    text=report['run']['stdout']
    report['original_sdk_handle_abi_verified']='NATIVE_ALLOC004_HANDLE_ABI original_sdk=1 header_bytes=56 reserve_offset=48 reserve_fds=2 reserve_ints=3' in text
    report['cpu_gpu_coherency_verified']=report['gpu_pixel_test_passed'] and all(
        f'NATIVE_ALLOC004_PIXEL sample={i} rgba=64,128,191,255' in text and
        f'NATIVE_ALLOC004_GPU_TO_CPU sample={i} rgba=191,64,128,255' in text for i in (0,1))
    report['fd_identity_warning_present']='os_same_file_description' in (text+report['run']['stderr'])
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['original_sdk_handle_abi_verified','cpu_gpu_coherency_verified','gpu_pixel_test_passed','fd_identity_warning_present','run','new_kernel_log']},indent=2))
