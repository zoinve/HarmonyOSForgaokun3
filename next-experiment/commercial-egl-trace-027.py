"""Reserve independent bounded diagnostic quotas for each real boundary."""
from pathlib import Path
import runpy
previous=runpy.run_path(str(Path(__file__).with_name('commercial-egl-trace-026.py')))
old='''    static unsigned calls=0;
    if (__atomic_add_fetch(&calls,1,__ATOMIC_RELAXED)<=64) {'''
new='''    static unsigned calls[6]={};
    const char *stages[]={"mesa","platform-entry","platform-symbol","drm-open","gbm-device","mesa-display"};
    unsigned slot=0;
    while (slot<6 && strcmp(stage,stages[slot])) ++slot;
    if (slot<6 && __atomic_add_fetch(&calls[slot],1,__ATOMIC_RELAXED)<=8) {'''
assert previous['HEADER'].count(old)==1
HEADER=previous['HEADER'].replace(old,new,1).replace('026','027')
def instrument(source):
    result=previous['instrument'](source)
    assert result.count(previous['HEADER'])==1
    return result.replace(previous['HEADER'],HEADER,1).replace('trace026','trace027').replace('drm_result026','drm_result027')
