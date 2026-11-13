"""Fresh 918: original authenticated HDC TCP trigger, no identity/state forgery."""
from pathlib import Path
import subprocess,runpy
base=Path(__file__).resolve().parent
out=base/'payload-918';assert not out.exists()
source=runpy.run_path(str(base/'hdc-probe.py'))['hdc_probe']((base/'payload-917/init.c').read_text())
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-918'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir();(out/'init.c').write_text(source)
files=[out/'init.c',base/'bounded-shell.c',base/'payload-913/gpu-present-snapshot.h',base/'payload-900/gpu-pixel-snapshot.h']
subprocess.run(['scp',*[str(p) for p in files],'matebook:'+remote+'/'],check=True)
subprocess.run(['ssh','matebook',f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'],check=True)
subprocess.run(['scp','matebook:'+remote+'/init',str(out/'init')],check=True)
setup=r'''
from pathlib import Path
import shutil,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883');work=root/'hdc-probe-918';work.mkdir()
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment');out=local/'payload-918'
ram=work/'ramroot';shutil.copytree(root/'aa-call-trace-917/ramroot',ram,symlinks=True)
shutil.copy2(out/'init',ram/'init')
'''
original=(base/'build-gpu-frontend-payload.py').read_text()
archive='def entry('+original.split('def entry(',1)[1].split("'''",1)[0]
archive=archive.replace("['init','gpu-frontend-probe']", "['init','gpu-frontend-probe','gpu903-allocator-probe','gpu912-window-probe']")
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=setup+archive,text=True,check=True)
