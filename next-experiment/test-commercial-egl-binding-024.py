"""Catch bridge self-calls escaping into a globally loaded EGL frontend.

The executable fixture characterizes ELF binding, not a working HarmonyOS GPU.
The actual AArch64 artifact is checked separately by the builder.
"""
from pathlib import Path
import runpy, subprocess, tempfile

base=Path(__file__).resolve().parent
module=base/'commercial-egl-binding-024.py'
assert module.exists(), 'missing EGL bridge link isolation'
isolate=runpy.run_path(str(module))['isolate_command']
script=r'''
from pathlib import Path
import runpy,subprocess,tempfile,json
isolate=runpy.run_path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/commercial-egl-binding-024.py')['isolate_command']
with tempfile.TemporaryDirectory(prefix='egl-binding-024-',dir='/home/zoinve/harmony-virgl-883') as tmp:
 p=Path(tmp)
 (p/'bridge.c').write_text('int eglGetPlatformDisplayEXT(void){return 17;} int eglGetDisplay(void){return eglGetPlatformDisplayEXT();}')
 (p/'front.c').write_text('#include <dlfcn.h>\nint eglGetPlatformDisplayEXT(void){return 99;} int main(int n,char **v){void *h=dlopen(v[1],RTLD_NOW|RTLD_LOCAL);if(!h)return 2;int (*f)(void)=dlsym(h,"eglGetDisplay");return f&&f()==17?0:3;}')
 subprocess.run(['cc','-rdynamic',str(p/'front.c'),'-ldl','-o',str(p/'front')],check=True)
 cmd=['cc','-shared','-fPIC',str(p/'bridge.c'),'-o',str(p/'bridge.so')]
 subprocess.run(cmd,check=True)
 old=subprocess.run([str(p/'front'),str(p/'bridge.so')]).returncode
 assert old==3,old
 subprocess.run(isolate(cmd,p/'fixed.so'),check=True)
 new=subprocess.run([str(p/'front'),str(p/'fixed.so')]).returncode
 assert new==0,new
 print(json.dumps(dict(baseline_interposed=True,isolated_self_call=True,target_gpu_test=False)))
'''
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script,text=True,timeout=60)
    raise SystemExit(result.returncode)
