"""Fresh 917: trace only own normal-shell aa clients, never alter their results."""
from pathlib import Path
import subprocess
base=Path(__file__).resolve().parent
out=base/'payload-917';assert not out.exists()
source=(base/'payload-916/init.c').read_text()
# Remove the entire root comparison; retain the proven zero-capability shell.
start=source.index('    if(count>0) {',source.index('static void direct916(void)'))
end=source.index('    for(int i=0;i<3;i++)',start)
source=source[:start]+source[end:]
# The now-unused root helper must not be compiled into the next diagnostic.
start=source.index('static int lab_root_run')
end=source.index('static int guide_count916',start)
source=source[:start]+source[end:]
start=source.index('static void direct916(void)')
end=source.index('static void command_probe(void)',start)
direct=source[start:end]
assert direct.count('"/system/bin/aa ')==2
direct=direct.replace('"/system/bin/aa ','"LD_PRELOAD=/system/lib64/lab-softpipe-167/gpu917-aa-trace.so /system/bin/aa ')
source=source[:start]+direct+source[end:]
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-917'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir();(out/'init.c').write_text(source)
files=[out/'init.c',base/'bounded-shell.c',base/'payload-913/gpu-present-snapshot.h',base/'payload-900/gpu-pixel-snapshot.h']
subprocess.run(['scp',*[str(p) for p in files],'matebook:'+remote+'/'],check=True)
subprocess.run(['ssh','matebook',f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'],check=True)
subprocess.run(['scp','matebook:'+remote+'/init',str(out/'init')],check=True)
setup=r'''
from pathlib import Path
import shutil,gzip,hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883');work=root/'aa-call-trace-917';work.mkdir()
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment');out=local/'payload-917'
ram=work/'ramroot';shutil.copytree(root/'direct-desktop-916/ramroot',ram,symlinks=True)
shutil.copy2(out/'init',ram/'init')
subprocess.run([str(root/'toolchain/ohos-cc'),'-O2','-Wall','-Wextra','-Werror','-shared','-fPIC',str(local/'aa-call-trace.c'),'-ldl','-Wl,-soname,gpu917-aa-trace.so','-o',str(ram/'gpu883-libs/gpu917-aa-trace.so')],check=True)
'''
original=(base/'build-gpu-frontend-payload.py').read_text()
archive='def entry('+original.split('def entry(',1)[1].split("'''",1)[0]
archive=archive.replace("['init','gpu-frontend-probe']", "['init','gpu-frontend-probe','gpu903-allocator-probe','gpu912-window-probe']")
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=setup+archive,text=True,check=True)
