"""Preserve433 and add passive per-channel discovery/outcome evidence."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
PRIOR = runpy.run_path(str(BASE / 'build-audio-native-433.py'))


def outer438(source, old_digest, digest):
    source = PRIOR['outer433'](source, old_digest, digest)
    old = '/commercial61-native-433/bootstrap-runtime087'
    assert old in source
    return source.replace(old, '/commercial61-native-438/bootstrap-runtime087')


def extra438(compile_program, stage, entries):
    PRIOR['PRIOR']['extra420'](compile_program, stage, entries)
    for name in ['native-bt-outcomes-435.h', 'native-bt-discovery-340.h']:
        (stage / name).open('xb').write((BASE / name).read_bytes())
    source = runpy.run_path(str(BASE / 'test-bt-outcomes-437.py'))['broker435']()
    compile_program('qca-broker435', source)
    entries['radio261/qca-broker'] = (0o100755, (stage / 'qca-broker435').read_bytes())


if __name__ == '__main__':
    original = PRIOR['PRIOR']['PRIOR']
    runpy.run_path(str(BASE / 'driver-builder-305.py'))['build'](
        438, original['runtime401'], outer438,
        original['OLD']['AUDIO']['RADIO']['vendor297'], extra438)
