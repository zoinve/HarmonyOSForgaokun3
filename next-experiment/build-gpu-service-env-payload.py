"""Fresh 897: remove only original RenderService software-driver overrides in RAM."""
import importlib.util
import json
import subprocess
from pathlib import Path

base = Path(__file__).resolve().parent
out = base / 'payload-897'
assert not out.exists()
spec = importlib.util.spec_from_file_location('service_env', base / 'gpu-service-env.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original = json.loads((base / 'gpu-runtime-883/original-graphic.cfg').read_text())
configuration = module.virgl_service_config(original)
source = (base / 'payload-896/init.c').read_text()
anchor = '    if(chdir("/newroot") || mount(".","/",NULL,MS_MOVE,NULL) || chroot(".") || chdir("/")) die("switch root mount");'
assert source.count(anchor) == 1
source = source.replace(anchor, '''
    if(mount("/gpu897-graphic.cfg","/newroot/system/etc/init/graphic.cfg",NULL,MS_BIND,NULL))die("GPU897 graphics config bind");
    if(mount(NULL,"/newroot/system/etc/init/graphic.cfg",NULL,MS_BIND|MS_REMOUNT|MS_RDONLY,NULL))die("GPU897 graphics config readonly");
    printf("GPU897_SERVICE_ENV software_overrides_removed=3 service_identity_preserved=1\\n");fflush(stdout);
''' + anchor)
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-897'
subprocess.run(['ssh', 'matebook', 'mkdir ' + remote], check=True)
out.mkdir()
(out / 'init.c').write_text(source)
(out / 'graphic.cfg').write_text(json.dumps(configuration, indent=2) + '\n')
subprocess.run(['scp', str(out / 'init.c'), str(base / 'bounded-shell.c'), 'matebook:' + remote + '/'], check=True)
subprocess.run(['ssh', 'matebook', f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'], check=True)
subprocess.run(['scp', 'matebook:' + remote + '/init', str(out / 'init')], check=True)
script = r'''
from pathlib import Path
import shutil,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883');work=root/'service-env-897';work.mkdir()
ram=work/'ramroot';shutil.copytree(root/'rendernode-trace-896/ramroot',ram,symlinks=True)
out=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-897')
shutil.copy2(out/'init',ram/'init');shutil.copy2(out/'graphic.cfg',ram/'gpu897-graphic.cfg')
'''
original_builder = (base / 'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + original_builder.split('def entry(', 1)[1].split("'''", 1)[0]
subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=script + archive, text=True, check=True)
