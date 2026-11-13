"""Test the diagnosed small-buffer stride hypothesis without changing target geometry."""
from pathlib import Path
import subprocess
payload=r'''
from pathlib import Path
import subprocess
r=Path('/home/zoinve/harmony-virgl-883');w=r/'native-gpu-probe-039';w.mkdir(exist_ok=False)
s=(r/'native-gpu-probe-037/gpu-probe-037.c').read_text()
assert s.count('ph=pass?2560:80')==1
s=s.replace('ph=pass?2560:80','ph=pass?2560:128',1)
(w/'gpu-probe-039.c').write_text(s)
subprocess.run(['aarch64-linux-gnu-gcc','-O2','-std=c11','-D_POSIX_C_SOURCE=200809L','-Wall','-Wextra','-Werror',
 '-I'+str(r/'prefix/system/include'),'-I'+str(r/'prefix/system/include/libdrm'),str(w/'gpu-probe-039.c'),'-ldl','-o',str(w/'gpu-probe')],check=True)
print('PASS: stride-hypothesis probe 039 compiled; original 1600x2560 test unchanged')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
