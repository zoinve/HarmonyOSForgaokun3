"""Deploy a new private DMA-BUF bundle and retain the proven nonroot render-only sandbox."""
from pathlib import Path
import json
import runpy
import subprocess

base=Path(__file__).resolve().parent.parent
package=base/'reports/baremetal-freedreno-dmabuf-package-001'
out=base/'reports/baremetal-freedreno-dmabuf-run-001'
first=runpy.run_path(str(base/'next-experiment/run-baremetal-freedreno-probe-001.py'),run_name='payload_only')['payload']
source=runpy.run_path(str(base/'next-experiment/run-baremetal-freedreno-probe-003.py'),run_name='payload_only')['source']
deployment=first[first.index("raw=Path("):first.index("props=['User=zoinve'")]
start=source.index("stage=Path('/var/lib/harmony-lab-freedreno-probe-001')")
end=source.index("props=['User=zoinve'",start)
source=source[:start]+deployment+source[end:]
for old,new in {
    'harmony-lab-freedreno-transfer-001':'harmony-lab-freedreno-dmabuf-transfer-001',
    'harmony-lab-freedreno-probe-001':'harmony-lab-freedreno-dmabuf-001',
    'harmony-lab-freedreno-sandbox-003':'harmony-lab-freedreno-dmabuf-sandbox-001',
    'harmony-lab-freedreno-probe-003':'harmony-lab-freedreno-dmabuf-probe-001',
    "{'lib','manifest.json'}":"{'lib','lib/gbm','manifest.json'}",
    "assert name=='probe' or (name.startswith('lib/') and len(Path(name).parts)==2)":
        "assert name=='probe' or name=='lib/gbm/dri_gbm.so' or (name.startswith('lib/') and len(Path(name).parts)==2 and Path(name).parts[1] not in ('.','..'))",
    'p.parent.mkdir(exist_ok=True)':'p.parent.mkdir(parents=True,exist_ok=True)',
    "'--setenv=EGL_LOG_LEVEL=debug']+args":
        "'--setenv=EGL_LOG_LEVEL=debug','--setenv=GBM_BACKEND=dri','--setenv=GBM_BACKENDS_PATH='+str(stage/'lib/gbm')]+args",
    'FREEDRENO001_PASS shader_triangle_and_readback desktop_not_tested=1':
        'DMABUF001_PASS gbm_dmabuf_egl_and_second_device_readback desktop_not_tested=1',
}.items():
    assert old in source,old
    source=source.replace(old,new)
anchor="assert set(members)==set(files)|set(links)|{'lib','lib/gbm','manifest.json'}"
source=source.replace(anchor,anchor+"\n    assert members['lib'].isdir() and members['lib/gbm'].isdir()")
compile(source,'dmabuf-native-run-001','exec')

if __name__=='__main__':
    expected=json.loads((package/'package.json').read_text())
    assert len(expected['files'])==9
    assert not out.exists();out.mkdir()
    prepare="from pathlib import Path;p=Path('/home/zoinve/harmony-lab-freedreno-dmabuf-transfer-001');assert not p.exists();p.mkdir(mode=0o700)"
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','python3 -'],input=prepare,text=True,capture_output=True,timeout=15)
    (out/'transfer-prepare.json').write_text(json.dumps(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2))
    r.check_returncode()
    subprocess.run(['scp',str(package/'bundle.tar.gz'),'matebook:/home/zoinve/harmony-lab-freedreno-dmabuf-transfer-001/bundle.tar.gz'],check=True,timeout=90)
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],
        input='expected='+repr(expected)+'\n'+source,text=True,capture_output=True,timeout=170)
    (out/'remote.stdout').write_text(r.stdout,encoding='utf-8');(out/'remote.stderr').write_text(r.stderr,encoding='utf-8')
    r.check_returncode();report=json.loads(r.stdout)
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(gpu_pixel_test_passed=report['gpu_pixel_test_passed'],run=report['run'],
                         effective_policy=report['effective_service_properties_before_probe'],
                         new_kernel_log=report['new_kernel_log'],desktop_verified=False),indent=2))
