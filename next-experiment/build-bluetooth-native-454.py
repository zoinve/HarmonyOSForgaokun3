"""Preserve438 integration with the tested transparent transport fix451."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
PRIOR = runpy.run_path(str(BASE / 'build-bluetooth-native-438.py'))


def outer454(source, old_digest, digest):
    source = PRIOR['outer438'](source, old_digest, digest)
    old = '/commercial61-native-438/bootstrap-runtime087'
    assert old in source
    return source.replace(old, '/commercial61-native-454/bootstrap-runtime087')


def extra454(compile_program, stage, entries):
    PRIOR['extra438'](compile_program, stage, entries)
    source = runpy.run_path(str(BASE / 'native-bt-transport-451.py'))['broker451']()
    compile_program('qca-broker451', source)
    entries['radio261/qca-broker'] = (0o100755, (stage / 'qca-broker451').read_bytes())


if __name__ == '__main__':
    original = PRIOR['PRIOR']['PRIOR']['PRIOR']
    runpy.run_path(str(BASE / 'driver-builder-305.py'))['build'](
        454, original['runtime401'], outer454,
        original['OLD']['AUDIO']['RADIO']['vendor297'], extra454)
