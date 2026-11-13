"""Keep only the renderer policy actually used by this allocator coherency probe."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
payload=runpy.run_path(str(base/'package-baremetal-buffer-vdi-003.py'))['payload']
head,sep,tail=payload.partition('\nfrom pathlib import Path')
assert sep
namespace={}
exec(compile(head,'private-probe-source-literals','exec'),namespace)
unused=(base/'baremetal-freedreno-policy-001.h').read_text().split('static int freedreno_pixels_ok',1)[1].split('#endif',1)[0]
unused='static inline int freedreno_pixels_ok'+unused
probe=namespace['probe'];assert probe.count(unused)==1
probe=probe.replace(unused,'')
payload='vdi='+repr(namespace['vdi'])+'\nprobe='+repr(probe)+sep+tail
for old,new in [('baremetal-buffer-vdi-003','baremetal-buffer-vdi-004'),
                ('baremetal-buffer-vdi-package-003','baremetal-buffer-vdi-package-004'),
                ('libnative-buffer-vdi-003.so','libnative-buffer-vdi-004.so'),('NATIVE_ALLOC003_','NATIVE_ALLOC004_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'native-buffer-vdi-package004','exec')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240).returncode)
