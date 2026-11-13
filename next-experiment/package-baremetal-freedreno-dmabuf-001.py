"""Package a fresh DMA-BUF probe and the matching GBM backend; never deploy here."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
out=base.parent/'reports/baremetal-freedreno-dmabuf-package-001'
old=runpy.run_path(str(base/'package-baremetal-freedreno-probe-001.py'),run_name='payload_only')['payload']
source=runpy.run_path(str(base/'baremetal-freedreno-dmabuf-probe-001.py'))['build_source']()
payload=('source='+repr(source)+'\nheader='+repr((base/'baremetal-freedreno-policy-001.h').read_text())+
         '\ndmabuf_header='+repr((base/'baremetal-freedreno-dmabuf-policy-001.h').read_text())+'\n'+
         old[old.index('from pathlib import Path\n'):])
payload=payload.replace('baremetal-freedreno-probe-package-001','baremetal-freedreno-dmabuf-package-001')
payload=payload.replace('baremetal-freedreno-probe-001','baremetal-freedreno-dmabuf-001')
payload=payload.replace('dst=libs/name;shutil.copyfile(src,dst);dst.chmod(0o555)',
                        'dst=libs/name;dst.parent.mkdir(exist_ok=True);shutil.copyfile(src,dst);dst.chmod(0o555)')
anchor="(work/'probe.c').write_text(source);"
assert payload.count(anchor)==1
payload=payload.replace(anchor,
 "copy(stage/'gbm/dri_gbm.so','gbm/dri_gbm.so','075f54cf2e92978c48b8e485436e135f95f9dfc6bb8c5273ac757a1c62887d49')\n"+
 "(work/'baremetal-freedreno-dmabuf-policy-001.h').write_text(dmabuf_header)\n"+anchor)
assert payload.count("'-lEGL','-lGLESv2'")==1
payload=payload.replace("'-lEGL','-lGLESv2'","'-lEGL','-lGLESv2','-lgbm'")
payload=payload.replace("build_command=args,gpu_execution_verified=False,desktop_verified=False)",
 "dmabuf_policy_sha256=sha(work/'baremetal-freedreno-dmabuf-policy-001.h'),build_command=args,gpu_execution_verified=False,desktop_verified=False)")
compile(payload,'dmabuf-package-001','exec')

if __name__=='__main__':
    assert not out.exists();out.mkdir()
    subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,check=True,timeout=120)
