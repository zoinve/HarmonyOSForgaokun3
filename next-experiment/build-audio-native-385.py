"""Fix378 initialization ordering; preserve its completed failure evidence."""
from pathlib import Path
import runpy
BASE=Path(__file__).resolve().parent
OLD=runpy.run_path(str(BASE/'build-audio-native-378.py'))

def runtime385(source):
    source=OLD['runtime378'](source)
    begin=source.index('    int jack378_library=')
    end=source.index('    commercial_vendor016();',begin)
    block=source[begin:end]
    assert 'audio378 trace placeholder' in block
    source=source[:begin]+source[end:]
    return OLD['ONCE'](source,'    commercial_vendor016();','    commercial_vendor016();\n'+block)

def outer385(source,old_digest,digest):
    return OLD['outer378'](source,old_digest,digest).replace(
        '/commercial61-native-378/bootstrap-runtime087','/commercial61-native-385/bootstrap-runtime087')

if __name__=='__main__':
    runpy.run_path(str(BASE/'driver-builder-305.py'))['build'](
        385,runtime385,outer385,OLD['AUDIO']['RADIO']['vendor297'],OLD['extra378'])
