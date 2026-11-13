"""Fresh 907: integrate the independently tested GBM VDI through a readonly RAM bind."""
from pathlib import Path
import subprocess, runpy

base = Path(__file__).resolve().parent
out = base/'payload-907'; assert not out.exists()
source = runpy.run_path(str(base/'gpu-allocator-overlay.py'))['allocator_overlay']((base/'payload-906/init.c').read_text())
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-907'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir();(out/'init.c').write_text(source)
subprocess.run(['scp',str(out/'init.c'),str(base/'bounded-shell.c'),str(base/'gpu-present-snapshot.h'),str(base/'payload-900/gpu-pixel-snapshot.h'),'matebook:'+remote+'/'],check=True)
subprocess.run(['ssh','matebook',f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'],check=True)
subprocess.run(['scp','matebook:'+remote+'/init',str(out/'init')],check=True)
script = r'''
from pathlib import Path
import subprocess,shutil,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883'); work=root/'allocator-overlay-907'; work.mkdir()
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment');out=local/'payload-907'
ram=work/'ramroot';shutil.copytree(root/'allocator-sync-906/ramroot',ram,symlinks=True)
shutil.copy2(out/'init',ram/'init')
'''
original = (base/'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + original.split('def entry(',1)[1].split("'''",1)[0]
archive = archive.replace("['init','gpu-frontend-probe']", "['init','gpu-frontend-probe','gpu903-allocator-probe']")
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script+archive,text=True,check=True)
