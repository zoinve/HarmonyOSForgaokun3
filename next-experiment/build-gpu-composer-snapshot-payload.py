"""Fresh 899: read Composer's existing client-buffer state; no drawing changes."""
from pathlib import Path
import subprocess

base=Path(__file__).resolve().parent
out=base/'payload-899';assert not out.exists()
source=(base/'payload-898/init.c').read_text()
anchor='#include "gpu-present-snapshot.h"'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'\n#include "gpu-composer-snapshot.h"')
assert source.count('    gpu898_snapshot();')==1
source=source.replace('    gpu898_snapshot();','    gpu898_snapshot();\n    gpu899_composer_snapshot();')
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-899'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir();(out/'init.c').write_text(source)
subprocess.run(['scp',str(out/'init.c'),str(base/'gpu-present-snapshot.h'),str(base/'gpu-composer-snapshot.h'),str(base/'bounded-shell.c'),'matebook:'+remote+'/'],check=True)
subprocess.run(['ssh','matebook',f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'],check=True)
subprocess.run(['scp','matebook:'+remote+'/init',str(out/'init')],check=True)
script=r'''
from pathlib import Path
import shutil,gzip,hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883');work=root/'composer-snapshot-899';work.mkdir()
ram=work/'ramroot';shutil.copytree(root/'present-result-898/ramroot',ram,symlinks=True)
out=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-899')
shutil.copy2(out/'init',ram/'init')
'''
original=(base/'build-gpu-frontend-payload.py').read_text()
archive='def entry('+original.split('def entry(',1)[1].split("'''",1)[0]
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script+archive,text=True,check=True)
