"""Host pixel/rotation regression; not proof of a physical input repair."""
from pathlib import Path
import subprocess
base=Path(__file__).resolve().parent
assert (base/'native-cursor-pixels-032.h').exists(),'missing real software cursor pixel path'
code=r'''
from pathlib import Path
import subprocess,tempfile
base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
with tempfile.TemporaryDirectory(prefix='cursor032-') as d:
 for name in ['test-native-cursor-032.cpp','test-native-cursor-adapter-032.cpp']:
  out=str(Path(d)/name)
  subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-g',str(base/name),'-ldl','-pthread','-o',out],check=True)
  subprocess.run([out],check=True)
print('PASS: clockwise physical coordinates, clipping, padding, hide/erase, screen isolation, buffer bounds (ASan/UBSan)')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=code,text=True).returncode)
