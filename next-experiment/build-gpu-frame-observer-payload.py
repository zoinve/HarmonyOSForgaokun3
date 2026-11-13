"""Fresh 913: unchanged GPU stack, bounded continuously readable framebuffer."""
from pathlib import Path
import subprocess,runpy
base=Path(__file__).resolve().parent
out=base/'payload-913';assert not out.exists()
source=(base/'payload-912/init.c').read_text()
anchor='    puts("GPU885_DONE desktop_not_tested=1");fflush(stdout);'
assert source.count(anchor)==1
source=source.replace(anchor,'    gpu913_observe();\n'+anchor)
header=runpy.run_path(str(base/'gpu-frame-observer.py'))['frame_observer']((base/'gpu-present-snapshot.h').read_text())
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-913'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir();(out/'init.c').write_text(source);(out/'gpu-present-snapshot.h').write_text(header)
subprocess.run(['scp',str(out/'init.c'),str(out/'gpu-present-snapshot.h'),str(base/'bounded-shell.c'),str(base/'payload-900/gpu-pixel-snapshot.h'),'matebook:'+remote+'/'],check=True)
subprocess.run(['ssh','matebook',f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'],check=True)
subprocess.run(['scp','matebook:'+remote+'/init',str(out/'init')],check=True)
setup=r'''
from pathlib import Path
import shutil,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883');work=root/'frame-observer-913';work.mkdir()
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment');out=local/'payload-913'
ram=work/'ramroot';shutil.copytree(root/'gbm-copy-912/ramroot',ram,symlinks=True)
shutil.copy2(out/'init',ram/'init')
'''
original=(base/'build-gpu-frontend-payload.py').read_text()
archive='def entry('+original.split('def entry(',1)[1].split("'''",1)[0]
archive=archive.replace("['init','gpu-frontend-probe']", "['init','gpu-frontend-probe','gpu903-allocator-probe','gpu912-window-probe']")
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=setup+archive,text=True,check=True)
