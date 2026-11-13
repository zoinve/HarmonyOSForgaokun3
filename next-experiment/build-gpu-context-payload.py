"""Fresh 887: observe RS backend environment and test real EGL contexts."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-887'
assert not out.exists()
source = (base / 'payload-886/init.c').read_text()
anchor = 'if(!strstr(name,"render_service"))continue;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + r'''
        snprintf(path,sizeof(path),"/proc/%.32s/environ",gpu_entry->d_name);
        f=fopen(path,"r");
        if(f) {
          char env[16385]={0};size_t n=fread(env,1,sizeof(env)-1,f);fclose(f);
          for(size_t i=0;i<n;) {
            size_t len=strnlen(env+i,n-i);
            if(!strncmp(env+i,"GBM_BACKENDS_PATH=",18)||!strncmp(env+i,"LD_LIBRARY_PATH=",16))
              printf("GPU887_RS_ENV %s\n",env+i);
            i+=len+1;
          }
        }
''')
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-887'
subprocess.run(['ssh', 'matebook', 'mkdir ' + remote], check=True)
out.mkdir()
(out / 'init.c').write_text(source)
subprocess.run(['scp', str(out/'init.c'), str(base/'bounded-shell.c'), 'matebook:'+remote+'/'], check=True)
subprocess.run(['ssh', 'matebook', f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'], check=True)
subprocess.run(['scp', 'matebook:'+remote+'/init', str(out/'init')], check=True)
original = (base/'build-gpu-frontend-payload.py').read_text()
script = original.split("script = r'''", 1)[1].split("'''", 1)[0]
script = script.replace('next-experiment/payload-885', 'next-experiment/payload-887')
script = script.replace("ram=root/'frontend-probe-885/ramroot';shutil.copytree(root/'system-overlay-883/ramroot',ram,symlinks=True)",
    "ram=root/'context-probe-887/ramroot';shutil.copytree(root/'gbm-probe-886/ramroot',ram,symlinks=True)")
script = script.replace("root/'frontend-probe-885/gpu-frontend-probe'", "root/'context-probe-887/gpu-frontend-probe'")
subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=script, text=True, check=True)
