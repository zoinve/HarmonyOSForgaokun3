"""Record actual own EGL surface/current/swap results without altering decisions."""
from pathlib import Path
import runpy
previous=runpy.run_path(str(Path(__file__).with_name('commercial-egl-trace-028.py')))
stages=previous['stages']+['eglCreateWindowSurface-exit','eglMakeCurrent-exit','eglSwapBuffers-exit']
HEADER=previous['HEADER'].replace('028','029').replace('calls[19]','calls[22]').replace('slot<19','slot<22')
old=','.join('"'+s+'"' for s in previous['stages'])
assert HEADER.count(old)==1
HEADER=HEADER.replace(old,','.join('"'+s+'"' for s in stages),1)

def instrument_returns(source):
    result=source
    arguments=['egl, config, native, attributes','egl, draw, read, context','egl, surface']
    for entry,args in zip(previous['ENTRIES'],arguments):
        assert result.count(entry)==1,entry
        signature=entry.removesuffix('\n{')
        name=signature.split('(')[0].split()[-1]
        local=signature.replace('extern "C"','static',1).replace(name+'(', 'observed029_'+name+'(',1)
        result=result.replace(entry,local+'\n{',1)
        result+='\n'+signature+'\n{\n    auto result029=observed029_'+name+'('+args+');\n    trace029("'+name+'-exit",(long)(uintptr_t)result029);\n    return result029;\n}\n'
    return result

def instrument(source):
    result=previous['instrument'](source)
    assert result.count(previous['HEADER'])==1
    result=result.replace(previous['HEADER'],HEADER,1).replace('trace028','trace029').replace('drm_result028','drm_result029')
    return instrument_returns(result)
