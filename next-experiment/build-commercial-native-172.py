"""Build the tested explicit data-mount teardown without changing native services."""
from pathlib import Path
import json
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
LIFECYCLE = runpy.run_path(str(BASE / 'persistent-lifecycle-172.py'))
PREVIOUS = runpy.run_path(str(BASE / 'build-commercial-native-168.py'))
runtime172 = PREVIOUS['runtime168']

def outer172(source, digest, filesystem_uuid):
    source = LIFECYCLE['outer172'](source, digest, filesystem_uuid)
    old = '/commercial61-native-168/bootstrap-runtime087'
    assert source.count(old) == 5
    return source.replace(old, '/commercial61-native-172/bootstrap-runtime087')

if __name__ == '__main__':
    recovered = json.loads((ROOT / 'reports/persistent-source-recovery-171/result.json').read_text())
    assert recovered['filesystem_clean'] and recovered['lab_partition_unmounted']
    checks = json.loads((ROOT / 'reports/persistent-lifecycle-172/result.json').read_text())
    assert checks['tests_exit'] == 0 and checks['inputs_unchanged']
    source = (BASE / 'build-commercial-native-166.py').read_text()
    source = source.replace('commercial61-native-166', 'commercial61-native-172')
    source = source.replace('ordered_chain_equals_full_166', 'ordered_chain_equals_full_172')
    source = source.replace("sha((BASE/'persistent-data-166.h').read_bytes())",
        "sha((BASE/'persistent-data-172.h').read_bytes())")
    source = source.replace("sha((BASE/'persistent-runtime-166.h').read_bytes())",
        "sha((BASE/'persistent-runtime-168.h').read_bytes())")
    anchor = "if __name__=='__main__':"
    assert source.count(anchor) == 1
    source = source.replace(anchor,
        "runtime166=runtime172\nouter166=outer172\n" + anchor, 1)
    exec(compile(source, 'build-commercial-native-172.generated.py', 'exec'),
        {'__name__': '__main__', '__file__': str(BASE / 'build-commercial-native-172.generated.py'),
         'runtime172': runtime172, 'outer172': outer172})
