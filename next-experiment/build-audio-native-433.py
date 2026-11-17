"""Package capture transport invalidation without changing frozen420 evidence."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
PRIOR = runpy.run_path(str(BASE / 'build-audio-native-420.py'))


def outer433(source, old_digest, digest):
    source = PRIOR['outer420'](source, old_digest, digest)
    old = '/commercial61-native-420/bootstrap-runtime087'
    assert old in source
    return source.replace(old, '/commercial61-native-433/bootstrap-runtime087')


if __name__ == '__main__':
    runpy.run_path(str(BASE / 'driver-builder-305.py'))['build'](
        433, PRIOR['PRIOR']['runtime401'], outer433,
        PRIOR['PRIOR']['OLD']['AUDIO']['RADIO']['vendor297'], PRIOR['extra420'])
