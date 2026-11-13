from pathlib import Path
import subprocess
base=Path(__file__).resolve().parent
assert (base/'native-rotation-034.h').is_file(),'missing rotation acceleration'
payload=r'''
import subprocess
from pathlib import Path
p=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
work=Path('/home/zoinve/harmony-virgl-883/native-rotation-034-tests');work.mkdir(exist_ok=True)
for compiler,flags,name in [('gcc',['-fsanitize=address,undefined'],'rotation-host'),('aarch64-linux-gnu-gcc',['-static'],'rotation-arm64')]:
 cmd=[compiler,'-O2','-std=c11','-D_POSIX_C_SOURCE=200809L','-Wall','-Wextra','-Werror']+flags+['-I'+str(p),str(p/'test-native-rotation-034.c'),'-o',str(work/name)]
 subprocess.run(cmd,check=True)
 if name=='rotation-host':subprocess.run([str(work/name)],check=True)
subprocess.run(['g++','-O2','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(p),str(p/'test-native-cached-034.cpp'),'-o',str(work/'cached-host')],check=True)
subprocess.run([str(work/'cached-host')],check=True)
print('PASS host pixel tests and AArch64 NEON compilation; ARM64 execution still required')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
