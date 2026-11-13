"""Run the isolated native-fence probe without changing the proven sandbox policy."""
from pathlib import Path
import json
import runpy
import subprocess

base=Path(__file__).resolve().parent.parent
package=base/'reports/baremetal-freedreno-fence-package-001'
out=base/'reports/baremetal-freedreno-fence-run-001'
source=runpy.run_path(str(base/'next-experiment/run-baremetal-freedreno-dmabuf-001.py'),run_name='payload_only')['source']
source=source.replace('harmony-lab-freedreno-dmabuf','harmony-lab-freedreno-fence')
source=source.replace('DMABUF001_PASS gbm_dmabuf_egl_and_second_device_readback desktop_not_tested=1',
                      'FENCE001_PASS native_fence_and_dmabuf_coherence desktop_not_tested=1')
compile(source,'native-fence-run-001','exec')

if __name__=='__main__':
    expected=json.loads((package/'package.json').read_text())
    assert not out.exists();out.mkdir()
    prepare="from pathlib import Path;p=Path('/home/zoinve/harmony-lab-freedreno-fence-transfer-001');assert not p.exists();p.mkdir(mode=0o700)"
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','python3 -'],input=prepare,text=True,capture_output=True,timeout=15)
    (out/'transfer-prepare.json').write_text(json.dumps(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2))
    r.check_returncode()
    subprocess.run(['scp',str(package/'bundle.tar.gz'),'matebook:/home/zoinve/harmony-lab-freedreno-fence-transfer-001/bundle.tar.gz'],check=True,timeout=90)
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],
        input='expected='+repr(expected)+'\n'+source,text=True,capture_output=True,timeout=170)
    (out/'remote.stdout').write_text(r.stdout,encoding='utf-8');(out/'remote.stderr').write_text(r.stderr,encoding='utf-8')
    r.check_returncode();report=json.loads(r.stdout)
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(gpu_pixel_test_passed=report['gpu_pixel_test_passed'],stdout=report['run']['stdout'],
                         returncode=report['run']['returncode'],new_kernel_log=report['new_kernel_log']),indent=2))
