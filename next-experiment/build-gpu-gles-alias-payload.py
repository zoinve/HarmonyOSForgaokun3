"""Fresh 891: product vendor-loader GLES names resolve to genuine Mesa drivers."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-891'
assert not out.exists()
out.mkdir()
script = r'''
from pathlib import Path
import shutil,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'gles-alias-probe-891';work.mkdir()
ram=work/'ramroot';shutil.copytree(root/'hook-probe-890/ramroot',ram,symlinks=True)
libs=ram/'gpu883-libs'
for alias,target in [('libGLESv1_impl.so','libGLESv1_CM.so.1'),
                     ('libGLESv2_impl.so','libGLESv2.so.2'),
                     ('libGLESv3_impl.so','libGLESv2.so.2')]:
 assert (libs/target).is_file()
 assert not (libs/alias).exists()
 (libs/alias).symlink_to(target)
out=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-891')
'''
original = (base / 'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + original.split('def entry(', 1)[1].split("'''", 1)[0]
subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
               input=script + archive, text=True, check=True)
