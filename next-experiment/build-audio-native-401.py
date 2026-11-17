"""Keep394 real jack integration and make only its private trace bind writable."""
from pathlib import Path
import runpy
BASE=Path(__file__).resolve().parent
PRIOR=runpy.run_path(str(BASE/'build-audio-native-394.py'))
OLD=PRIOR['OLD'];ONCE=PRIOR['ONCE']

def runtime401(source):
    source=PRIOR['runtime394'](source)
    anchor='    dprintf(1,"AUDIO378_DETECTOR'
    binding=r'''    int trace401=open("/audio376/jack.trace",O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0600);
    if(trace401<0||fchown(trace401,1041,1041)||close(trace401))fail("audio401 private trace source");
    if(mount("/audio376/jack.trace","/vendor/lib64/harmony-graphics/audio-jack376.trace",NULL,MS_BIND,NULL))
        fail("audio401 private trace writable bind");
    dprintf(1,"AUDIO401_TRACE private_uid=1041 mode=0600 readonly_vendor_preserved=1 authentication_unchanged=1\n");
'''
    return ONCE(source,anchor,binding+anchor)

def outer401(source,old_digest,digest):
    return PRIOR['outer394'](source,old_digest,digest).replace(
        '/commercial61-native-394/bootstrap-runtime087','/commercial61-native-401/bootstrap-runtime087')

if __name__=='__main__':
    runpy.run_path(str(BASE/'driver-builder-305.py'))['build'](
        401,runtime401,outer401,OLD['AUDIO']['RADIO']['vendor297'],OLD['extra378'])
