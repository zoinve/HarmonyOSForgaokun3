"""Preserve401 integration and add tested real-capture/shared-card backend."""
from pathlib import Path
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
PRIOR = runpy.run_path(str(BASE/'build-audio-native-401.py'))
BUILD = PRIOR['OLD']['AUDIO']['BUILD']

def outer420(source, old_digest, digest):
    source = PRIOR['outer401'](source, old_digest, digest)
    assert '/commercial61-native-401/bootstrap-runtime087' in source
    return source.replace('/commercial61-native-401/bootstrap-runtime087',
                          '/commercial61-native-420/bootstrap-runtime087')

def extra420(compile_program, stage, entries):
    PRIOR['OLD']['extra378'](compile_program, stage, entries)
    for name in ['native-audio-protocol-412.h', 'native-audio-card-410.h',
                 'native-audio-session-411.h', 'native-audio-workers-411.h',
                 'native-audio-capture-client-413.h', 'native-audio-capture-vdi-413.h']:
        (stage/name).open('xb').write((BASE/name).read_bytes())
    server = stage/'audio-duplex-server411.c'
    server.open('x').write(runpy.run_path(str(BASE/'native-audio-server-411.py'))['server411']())
    vendor = stage/'audio-capture-vdi414.c'
    vendor.open('x').write(runpy.run_path(str(BASE/'native-audio-vdi-414.py'))['vendor414']())
    flags = ['-O2', '-Wall', '-Wextra', '-Werror', '-I', str(stage)]
    executable = stage/'audio-duplex-server411'
    subprocess.run(['aarch64-linux-gnu-gcc', *flags, str(server), '-ldl', '-pthread',
                    '-o', str(executable)], check=True)
    library = stage/'libaudio_capture414.z.so'
    subprocess.run([str(BUILD/'window-bridge/toolchain/ohos-cc'), *flags,
                    '-I', str(BUILD/'audio-contract-314-peripheral/audio/interfaces/sound/v1_0'),
                    '-shared', '-fPIC', '-Wl,--no-undefined,-soname,libaudio_primary_impl.z.so',
                    str(vendor), '-o', str(library)], check=True)
    symbols = subprocess.check_output(['readelf', '--dyn-syms', '--wide',
        str(BUILD/'audio-assets-314/lib/libasound.so.2')], text=True)
    assert any(line.split()[-1].split('@')[0]=='snd_pcm_readi' and line.split()[6]!='UND'
               for line in symbols.splitlines() if len(line.split())>=8)
    entries['audio315/server'] = (0o100755, executable.read_bytes())
    entries['native-target/audio315/libaudio_primary_impl.z.so'] = (0o100755, library.read_bytes())

if __name__ == '__main__':
    runpy.run_path(str(BASE/'driver-builder-305.py'))['build'](
        420, PRIOR['runtime401'], outer420, PRIOR['OLD']['AUDIO']['RADIO']['vendor297'], extra420)
