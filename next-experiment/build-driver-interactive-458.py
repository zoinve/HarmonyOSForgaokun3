"""Latest454 drivers with a bounded manual acceptance window, Ubuntu unchanged."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
PRIOR = runpy.run_path(str(BASE / 'build-bluetooth-native-454.py'))


def outer458(source, old_digest, digest):
    source = PRIOR['outer454'](source, old_digest, digest)
    old = '/commercial61-native-454/bootstrap-runtime087'
    assert old in source
    source = source.replace(old, '/commercial61-native-458/bootstrap-runtime087')
    old_budget = '360, 120, requested'
    assert source.count(old_budget) == 1
    return source.replace(old_budget, '900, 120, requested')


if __name__ == '__main__':
    original = PRIOR['PRIOR']['PRIOR']['PRIOR']['PRIOR']
    runpy.run_path(str(BASE / 'driver-builder-305.py'))['build'](
        458, original['runtime401'], outer458,
        original['OLD']['AUDIO']['RADIO']['vendor297'], PRIOR['extra454'])
