"""Integrate explicit speaker/headphone routing; retain original-service playback probe."""
from pathlib import Path
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
OLD=runpy.run_path(str(BASE/'build-audio-native-353.py'))
AUDIO=OLD['AUDIO']
def outer365(source,old_digest,digest):
 return OLD['outer353'](source,old_digest,digest).replace(
   '/commercial61-native-353/bootstrap-runtime087','/commercial61-native-365/bootstrap-runtime087')
def extra365(compile_program,stage,entries):
 for name in ['native-audio-protocol-315.h','native-audio-client-317.h',
              'native-audio-metrics-349.h','native-audio-route-vdi-363.h']:
  (stage/name).open('xb').write((BASE/name).read_bytes())
 OLD['extra353'](compile_program,stage,entries)
 source=runpy.run_path(str(BASE/'native-audio-vdi-363.py'))['vendor363']()
 path=stage/'audio-route-vdi363.c';path.open('x').write(source)
 headers=AUDIO['BUILD']/'audio-contract-314-peripheral/audio/interfaces/sound/v1_0'
 compiler=str(AUDIO['BUILD']/'window-bridge/toolchain/ohos-cc')
 library=stage/'libaudio_primary_impl.z.so'
 subprocess.run([compiler,'-O2','-Wall','-Wextra','-Werror','-I',str(stage),'-I',str(BASE),
   '-I',str(headers),'-shared','-fPIC','-Wl,--no-undefined,-soname,libaudio_primary_impl.z.so',
   str(path),'-o',str(library)],check=True)
 entries['native-target/audio315/libaudio_primary_impl.z.so']=(0o100755,library.read_bytes())
if __name__=='__main__':
 runpy.run_path(str(BASE/'driver-builder-305.py'))['build'](
   365,AUDIO['runtime321'],outer365,AUDIO['RADIO']['vendor297'],extra365)
