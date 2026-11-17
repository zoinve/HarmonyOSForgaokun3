"""Host process and capacity tests; no SSH, disk formatting or reboot."""
import subprocess
payload=r'''
from pathlib import Path
import subprocess
base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
assert (base/'commercial-safety-010.h').is_file(),'missing bounded cleanup and memory admission'
work=Path('/home/zoinve/harmony-virgl-883/commercial-safety-010-tests');work.mkdir(exist_ok=True)
subprocess.run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-I'+str(base),str(base/'test-commercial-safety-010.c'),'-o',str(work/'safety-test')],check=True)
subprocess.run([str(work/'safety-test')],check=True,timeout=5)
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
