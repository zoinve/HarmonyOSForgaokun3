"""Observe post-display EGL forwarding without changing its real results."""
from pathlib import Path
import runpy
previous=runpy.run_path(str(Path(__file__).with_name('commercial-egl-trace-027.py')))
stages=['mesa','platform-entry','platform-symbol','drm-open','gbm-device','mesa-display']
for name in ['eglInitialize','eglChooseConfig','eglGetConfigs','eglCreateContext','eglCreatePbufferSurface']:
    stages.extend([name+'-entry',name+'-exit'])
stages.extend(['eglCreateWindowSurface-entry','eglMakeCurrent-entry','eglSwapBuffers-entry'])
HEADER=previous['HEADER'].replace('027','028').replace('calls[6]','calls[19]').replace('slot<6','slot<19')
old='"mesa","platform-entry","platform-symbol","drm-open","gbm-device","mesa-display"'
assert HEADER.count(old)==1
HEADER=HEADER.replace(old,','.join('"'+stage+'"' for stage in stages),1)
OLD_FORWARD='#define FORWARD(ret, name, signature, arguments, fallback) '+chr(92)+'\n'+'extern "C" ret name signature { auto fn = real<decltype(&name)>(#name); return fn ? fn arguments : fallback; }'
NEW_FORWARD='#define FORWARD(ret, name, signature, arguments, fallback) '+chr(92)+'\n'+'extern "C" ret name signature { trace028(#name "-entry",0); auto fn = real<decltype(&name)>(#name); ret result028=fn ? fn arguments : fallback; trace028(#name "-exit",(long)(uintptr_t)result028); return result028; }'
ENTRIES=[
    'extern "C" EGLSurface eglCreateWindowSurface(EGLDisplay egl, EGLConfig config, EGLNativeWindowType native, const EGLint *attributes)\n{',
    'extern "C" EGLBoolean eglMakeCurrent(EGLDisplay egl, EGLSurface draw, EGLSurface read, EGLContext context)\n{',
    'extern "C" EGLBoolean eglSwapBuffers(EGLDisplay egl, EGLSurface surface)\n{']
def instrument_forward(source):
    assert source.count(OLD_FORWARD)==1
    result=source.replace(OLD_FORWARD,NEW_FORWARD,1)
    for entry in ENTRIES:
        assert result.count(entry)==1,entry
        name=entry.split('(')[0].split()[-1]
        result=result.replace(entry,entry+'\n    trace028("'+name+'-entry",0);',1)
    return result
def instrument(source):
    result=previous['instrument'](source)
    assert result.count(previous['HEADER'])==1
    result=result.replace(previous['HEADER'],HEADER,1).replace('trace027','trace028').replace('drm_result027','drm_result028')
    return instrument_forward(result)
