from pathlib import Path
import subprocess
assert Path(__file__).with_name('native-gpu-composer-041.h').is_file(), 'missing native GPU composer helper'
payload=r'''
from pathlib import Path
import subprocess
root=Path('/home/zoinve/harmony-virgl-883');base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
work=root/'native-gpu-composer-041-tests';work.mkdir(exist_ok=True)
private=root/'native-gpu-composer-041-toolchain/sysroot'
inc=private/'usr/aarch64-linux-gnu/include/c++/14'
cmd=['clang++-19','--target=aarch64-linux-gnu','--gcc-toolchain=/usr','-nostdinc++','-isystem',str(inc),'-isystem',str(inc/'aarch64-linux-gnu'),'-L'+str(private/'usr/lib/gcc-cross/aarch64-linux-gnu/14'),'-O2','-std=c++17','-Wall','-Wextra','-Werror','-I'+str(base),'-I'+str(root/'prefix/system/include'),'-I'+str(root/'prefix/system/include/libdrm'),str(base/'test-native-gpu-composer-041.cpp'),'-ldl','-pthread','-o',str(work/'gpu-composer-test')]
# Private extracted Debian headers, no host/target package installation.
subprocess.run(cmd,check=True)
print('PASS: actual AArch64 GPU helper and real pixel/lifetime test compiled (not executed)')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
