"""Observe the real USB drive without changing node exposure or original services."""
from pathlib import Path
import hashlib
import json
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
PREVIOUS = runpy.run_path(str(BASE / 'build-commercial-native-173.py'))
runtime174 = PREVIOUS['runtime173']


def outer174(source, digest, filesystem_uuid):
    source = PREVIOUS['outer173'](source, digest, filesystem_uuid)
    old = '/commercial61-native-173/bootstrap-runtime087'
    assert source.count(old) == 5
    source = source.replace(old, '/commercial61-native-174/bootstrap-runtime087')
    include = '#include "native-service-devices-152.h"'
    assert source.count(include) == 1
    source = source.replace(include, include + '\n#include "native-usb-storage-174.h"', 1)
    anchor = '    native_service152_observe();'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '\n    native_usb_storage174_observe(child);', 1)
    anchor = '            for(unsigned elapsed033=70;elapsed033<150;++elapsed033){'
    assert source.count(anchor) == 1
    return source.replace(anchor, anchor + '\n                native_usb_storage174_observe(child);', 1)


if __name__ == '__main__':
    offline = json.loads((ROOT / 'reports/commercial61-native-173/persistent-offline-verification.json').read_text())
    assert offline['filesystem_clean'] and offline['lab_partition_unmounted']
    source = (BASE / 'build-commercial-native-166.py').read_text()
    source = source.replace('commercial61-native-166', 'commercial61-native-174')
    source = source.replace('ordered_chain_equals_full_166', 'ordered_chain_equals_full_174')
    source = source.replace("sha((BASE/'persistent-data-166.h').read_bytes())", "sha((BASE/'persistent-data-172.h').read_bytes())")
    source = source.replace("sha((BASE/'persistent-runtime-166.h').read_bytes())", "sha((BASE/'persistent-runtime-173.h').read_bytes())")
    anchor = "if __name__=='__main__':"
    assert source.count(anchor) == 1
    source = source.replace(anchor, 'runtime166=runtime174\nouter166=outer174\n' + anchor, 1)
    exec(compile(source, 'build-commercial-native-174.generated.py', 'exec'),
         {'__name__':'__main__', '__file__':str(BASE / 'build-commercial-native-174.generated.py'),
          'runtime174':runtime174, 'outer174':outer174})
