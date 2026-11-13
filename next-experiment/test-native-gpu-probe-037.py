"""036 chose an unavailable GBM pbuffer config; 037 requires no window surface."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('test-native-gpu-probe-036.py')))['payload']
payload=payload.replace("w=r/'native-gpu-probe-036'","w=r/'native-gpu-probe-037'")
anchor="cmd=['aarch64-linux-gnu-gcc'"
addition=r'''
source=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/native-gpu-probe-036.c').read_text()
assert source.count('EGL_SURFACE_TYPE,EGL_PBUFFER_BIT,EGL_RENDERABLE_TYPE')==1
source=source.replace('EGL_SURFACE_TYPE,EGL_PBUFFER_BIT,EGL_RENDERABLE_TYPE','EGL_SURFACE_TYPE,0,EGL_RENDERABLE_TYPE',1)
(w/'gpu-probe-037.c').write_text(source)
'''
payload=payload.replace(anchor,addition+'\n'+anchor,1)
payload=payload.replace(" '/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/native-gpu-probe-036.c','-ldl'", " str(w/'gpu-probe-037.c'),'-ldl'")
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
