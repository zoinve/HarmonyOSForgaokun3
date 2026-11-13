"""Build fresh 883 RAM-only VirGL/NativeWindow integration; no image writes."""
from pathlib import Path
import runpy
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-883'
assert not out.exists()
source = runpy.run_path(str(base / 'gpu-overlay.py'))['gpu_overlay'](
    (base / 'payload-881/init.c').read_text())
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-883'
subprocess.run(['ssh', 'matebook', 'mkdir ' + remote], check=True)
out.mkdir()
(out / 'init.c').write_text(source)
subprocess.run(['scp', str(out / 'init.c'), str(base / 'bounded-shell.c'), 'matebook:' + remote + '/'], check=True)
subprocess.run(['ssh', 'matebook', f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'], check=True)
subprocess.run(['scp', 'matebook:' + remote + '/init', str(out / 'init')], check=True)
script = r'''
from pathlib import Path
import gzip,hashlib,json,shutil,subprocess
root=Path('/home/zoinve/harmony-virgl-883')
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-883')
work=root/'system-overlay-883'
work.mkdir(exist_ok=False)
previous=root/'window-bridge'
source=(previous/'egl_window_bridge.cpp').read_text()
assert source.count('/system/lib64/lab-virgl883/')==1
(work/'egl_window_bridge.cpp').write_text(source.replace('/system/lib64/lab-virgl883/','/system/lib64/lab-softpipe-167/'))
prefix=root/'prefix/system'
with (work/'bridge-build.log').open('w') as log:
 subprocess.run([str(previous/'toolchain/ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17',
  '-Wall','-Wextra','-DEGL_EGLEXT_PROTOTYPES','-I'+str(previous),'-I'+str(previous/'include'),
  '-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),
  str(work/'egl_window_bridge.cpp'),str(previous/'drm_device.o'),
  '-L'+str(prefix/'lib64/lab-virgl883'),'-lGLESv2','-lgbm','-ldrm','-ldl',
  '-Wl,--no-undefined,-soname,libEGL_impl.so','-Wl,-Bsymbolic-functions',
  '-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(work/'libEGL_impl.so')],
  stdout=log,stderr=subprocess.STDOUT,check=True)
ram=work/'ramroot';libs=ram/'gpu883-libs';libs.mkdir(parents=True)
shutil.copy2(local/'init',ram/'init')
for p in (prefix/'lib64/lab-virgl883').iterdir():
 if '.so' not in p.name or p.name.endswith('.so') and p.name!='libgallium-25.0.1.so': continue
 if p.is_symlink(): (libs/p.name).symlink_to(p.readlink())
 else: shutil.copy2(p,libs/p.name)
shutil.copy2(root/'userspace-ramroot/system/lib64/lab-virgl883/libc++_shared.so',libs/'libc++_shared.so')
shutil.copy2(work/'libEGL_impl.so',libs/'libEGL_impl.so')
assert not (libs/'libEGL.so').exists() and not (libs/'libc.so').exists()
def entry(name,data,mode,ino):
 n=name.encode()+b'\0';fields=[ino,mode,0,0,1,0,len(data),0,0,0,0,len(n),0]
 b=b'070701'+b''.join(f'{v:08x}'.encode() for v in fields)+n
 b+=b'\0'*(-len(b)%4);b+=data;b+=b'\0'*(-len(data)%4)
 return b
raw=b'';files=[]
for i,p in enumerate(sorted(ram.rglob('*')),1):
 name=str(p.relative_to(ram))
 if p.is_symlink(): data=str(p.readlink()).encode();mode=0o120777
 elif p.is_dir(): data=b'';mode=0o040755
 else: data=p.read_bytes();mode=0o100755 if name=='init' else 0o100444
 raw+=entry(name,data,mode,i)
 files.append(dict(path=name,mode=oct(mode),sha256=hashlib.sha256(data).hexdigest()))
raw+=entry('TRAILER!!!',b'',0,len(files)+1)
target=local/'initramfs.cpio.gz';assert not target.exists()
target.write_bytes(gzip.compress(raw,mtime=0))
manifest=dict(sha256=hashlib.sha256(target.read_bytes()).hexdigest(),files=files,
 original_egl_frontend_preserved=True,sdk_libc_included=False,desktop_verified=False)
(local/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:v for k,v in manifest.items() if k!='files'}))
'''
subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=script, text=True, check=True)
