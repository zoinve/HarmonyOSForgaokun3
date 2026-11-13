"""Link the private bundle's actual versioned SONAMEs; preserve failed 001/002 outputs."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('package-baremetal-buffer-vdi-002.py')))['payload']
for old,new in [('baremetal-buffer-vdi-002','baremetal-buffer-vdi-003'),
                ('baremetal-buffer-vdi-package-002','baremetal-buffer-vdi-package-003'),
                ('libnative-buffer-vdi-002.so','libnative-buffer-vdi-003.so'),('NATIVE_ALLOC002_','NATIVE_ALLOC003_'),
                ("'-lgbm'","'-l:libgbm.so.1'"),("'-ldrm'","'-l:libdrm.so.2'"),
                ("'-lEGL'","'-l:libEGL.so.1'"),("'-lGLESv2'","'-l:libGLESv2.so.2'")]:
    assert old in payload,old
    payload=payload.replace(old,new)
anchor='manifest=dict(files=files,commands=commands,'
assert payload.count(anchor)==1
payload=payload.replace(anchor,"manifest=dict(files=files,symlinks={'lib/libc.so':'ld-musl-aarch64.so.1'},commands=commands,")
compile(payload,'native-buffer-vdi-package003','exec')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240).returncode)
