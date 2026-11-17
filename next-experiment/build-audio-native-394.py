"""Stage detector config in the final system overlay rather than its hidden lower."""
from pathlib import Path
import runpy

BASE=Path(__file__).resolve().parent
PRIOR=runpy.run_path(str(BASE/'build-audio-native-385.py'))
OLD=PRIOR['OLD'];ONCE=OLD['ONCE']

def runtime394(source):
    source=PRIOR['runtime385'](source)
    begin=source.index('    const char *jack378_sources[]=')
    end=source.index('    dprintf(1,"AUDIO378_DETECTOR',begin)
    block=source[begin:end]
    block=ONCE(block,',"/audio376/audio_server.cfg"','')
    block=ONCE(block,',"/system/etc/init/audio_server.cfg"','')
    block=ONCE(block,'i<2','i<1')
    source=source[:begin]+block+source[end:]
    anchor='    directory("/run/commercial-system005/upper/etc/init",0755);'
    return ONCE(source,anchor,anchor+'\n    commercial_copy005("/audio376/audio_server.cfg",'+
        '"/run/commercial-system005/upper/etc/init/audio_server.cfg",0644);')

def outer394(source,old_digest,digest):
    source=PRIOR['outer385'](source,old_digest,digest).replace(
        '/commercial61-native-385/bootstrap-runtime087','/commercial61-native-394/bootstrap-runtime087')
    helper=(BASE/'native-audio-jack-config-393.h').read_text()
    source=ONCE(source,'static void audio376_observe(pid_t target)',helper+'\nstatic void audio376_observe(pid_t target)')
    return ONCE(source,'        unsigned maps=0,jacks=0,threads=0;',
        '        audio393_config(pid);\n        unsigned maps=0,jacks=0,threads=0;')

if __name__=='__main__':
    runpy.run_path(str(BASE/'driver-builder-305.py'))['build'](
        394,runtime394,outer394,OLD['AUDIO']['RADIO']['vendor297'],OLD['extra378'])
