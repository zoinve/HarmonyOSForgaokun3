from pathlib import Path
import subprocess
base=Path(__file__).resolve().parent
assert (base/'native-gpu-probe-036.c').exists(),'missing real DMA-BUF GPU rotation probe'
payload=r'''
from pathlib import Path
import subprocess
r=Path('/home/zoinve/harmony-virgl-883');w=r/'native-gpu-probe-036'
w.mkdir(exist_ok=True)
cmd=['aarch64-linux-gnu-gcc','-O2','-std=c11','-D_POSIX_C_SOURCE=200809L','-Wall','-Wextra','-Werror',
 '-I'+str(r/'prefix/system/include'),'-I'+str(r/'prefix/system/include/libdrm'),
 '/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/native-gpu-probe-036.c','-ldl','-o',str(w/'gpu-probe')]
subprocess.run(cmd,check=True)
print('PASS: AArch64 probe compiled; real hardware pixel tests and performance NOT YET RUN')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
