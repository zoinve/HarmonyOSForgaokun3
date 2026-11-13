"""Private exec-separated DMA-BUF/fence test, unchanged live render-only sandbox."""
from pathlib import Path
import json
import runpy
import subprocess

base=Path(__file__).resolve().parent.parent
package=base/'reports/baremetal-freedreno-ipc-package-002'
out=base/'reports/baremetal-freedreno-ipc-run-002'
source=runpy.run_path(str(base/'next-experiment/run-baremetal-freedreno-fence-002.py'),run_name='payload_only')['source']
for old,new in [('harmony-lab-freedreno-fence-002','harmony-lab-freedreno-ipc-002'),
                ('harmony-lab-freedreno-fence-transfer-002','harmony-lab-freedreno-ipc-transfer-002'),
                ('harmony-lab-freedreno-fence-sandbox-002','harmony-lab-freedreno-ipc-sandbox-002'),
                ('harmony-lab-freedreno-fence-probe-002','harmony-lab-freedreno-ipc-probe-002'),
                ('FENCE001_PASS native_fence_and_dmabuf_coherence desktop_not_tested=1',
                 'IPC002_PASS cross_process_dmabuf_and_native_fence desktop_not_tested=1')]:
    assert old in source,old
    source=source.replace(old,new)
compile(source,'ipc002-render-only-remote','exec')
if __name__=='__main__':
    expected=json.loads((package/'package.json').read_text())
    assert len(expected['files'])==9 and expected['all_strong_dynamic_symbols_resolved']
    assert not out.exists();out.mkdir()
    prepare="from pathlib import Path;p=Path('/home/zoinve/harmony-lab-freedreno-ipc-transfer-002');assert not p.exists();p.mkdir(mode=0o700)"
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','python3 -'],input=prepare,text=True,capture_output=True,timeout=15)
    (out/'transfer-prepare.json').write_text(json.dumps(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2));r.check_returncode()
    subprocess.run(['scp',str(package/'bundle.tar.gz'),'matebook:/home/zoinve/harmony-lab-freedreno-ipc-transfer-002/bundle.tar.gz'],check=True,timeout=90)
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],input='expected='+repr(expected)+'\n'+source,text=True,capture_output=True,timeout=170)
    (out/'remote.stdout').write_text(r.stdout,encoding='utf-8');(out/'remote.stderr').write_text(r.stderr,encoding='utf-8')
    r.check_returncode();report=json.loads(r.stdout)
    text=report['run']['stdout'];warning='os_same_file_description' in report['run']['stderr']
    report['fd_identity_warning_present']=warning
    report['cross_process_gpu_execution_verified']=bool(report['gpu_pixel_test_passed'] and 'exec_consumer=1' in text and 'sender_transfer_fds_closed=1' in text and 'consumer_imported_fd_closed=1' in text)
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(returncode=report['run']['returncode'],stdout=text,stderr_bytes=len(report['run']['stderr'].encode()),fd_identity_warning_present=warning,cross_process_gpu_execution_verified=report['cross_process_gpu_execution_verified'],new_kernel_log=report['new_kernel_log']),indent=2))
