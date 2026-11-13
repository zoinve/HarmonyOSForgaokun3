"""Fresh 902: independent ION/dumb/GBM EGLImage comparison, services unchanged."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-902'
assert not out.exists()
out.mkdir()
script = r'''
from pathlib import Path
import shutil,subprocess,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'buffer-import-902';work.mkdir()
ram=work/'ramroot';shutil.copytree(root/'image-trace-901/ramroot',ram,symlinks=True)
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
probe=(local/'gpu-context-probe.c').read_text()
probe=probe.replace('#define EGL_LOAD', '#include "gpu-buffer-import-probe.h"\n\n#define EGL_LOAD',1)
anchor='    puts("GPU887_PASS product_frontend_context_readback desktop_not_tested=1");'
assert probe.count(anchor)==1
probe=probe.replace(anchor,anchor+'\n    gpu902_buffers(lib, display);')
(work/'probe.c').write_text(probe)
shutil.copy2(local/'gpu-buffer-import-probe.h',work)
prefix=root/'prefix/system';libs=prefix/'lib64/lab-virgl883'
subprocess.run([str(root/'toolchain/ohos-cc'),'-O2','-Wall','-Wextra','-Werror',
 '-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),
 str(work/'probe.c'),'-L'+str(libs),'-lgbm','-ldrm','-ldl',
 '-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(work/'gpu-frontend-probe')],check=True)
shutil.copy2(work/'gpu-frontend-probe',ram/'gpu883-libs/gpu-frontend-probe')
out=local/'payload-902'
'''
original = (base / 'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + original.split('def entry(', 1)[1].split("'''", 1)[0]
subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
               input=script + archive, text=True, check=True)
