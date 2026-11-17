"""Archive per-boot diagnostic logs and FIFOs while retaining the tested teardown."""
from pathlib import Path
import json
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
PREVIOUS = runpy.run_path(str(BASE / 'build-commercial-native-172.py'))

def runtime173(source):
    source = PREVIOUS['runtime172'](source)
    assert source.count('#include "persistent-runtime-168.h"') == 1
    return source.replace('persistent-runtime-168.h','persistent-runtime-173.h').replace(
        'persistent_runtime168();','persistent_runtime173();')

def outer173(source, digest, filesystem_uuid):
    source = PREVIOUS['outer172'](source, digest, filesystem_uuid)
    old = '/commercial61-native-172/bootstrap-runtime087'
    assert source.count(old) == 5
    return source.replace(old, '/commercial61-native-173/bootstrap-runtime087')

if __name__ == '__main__':
    recovered = json.loads((ROOT / 'reports/persistent-source-recovery-171/result.json').read_text())
    assert recovered['filesystem_clean'] and recovered['lab_partition_unmounted']
    source = (BASE / 'build-commercial-native-166.py').read_text()
    source = source.replace('commercial61-native-166','commercial61-native-173')
    source = source.replace('ordered_chain_equals_full_166','ordered_chain_equals_full_173')
    source = source.replace("sha((BASE/'persistent-data-166.h').read_bytes())",
        "sha((BASE/'persistent-data-172.h').read_bytes())")
    source = source.replace("sha((BASE/'persistent-runtime-166.h').read_bytes())",
        "sha((BASE/'persistent-runtime-173.h').read_bytes())")
    anchor = "if __name__=='__main__':"
    assert source.count(anchor) == 1
    source = source.replace(anchor,'runtime166=runtime173\nouter166=outer173\n' + anchor,1)
    exec(compile(source,'build-commercial-native-173.generated.py','exec'),
        {'__name__':'__main__','__file__':str(BASE / 'build-commercial-native-173.generated.py'),
         'runtime173':runtime173,'outer173':outer173})
