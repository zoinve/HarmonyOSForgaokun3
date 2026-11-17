"""Guard the identified USB medium before original-service startup."""
from pathlib import Path
import json
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
PREVIOUS = runpy.run_path(str(BASE / 'build-commercial-native-174.py'))
runtime175 = PREVIOUS['runtime174']


def outer175(source, digest, filesystem_uuid):
    source = PREVIOUS['outer174'](source, digest, filesystem_uuid)
    old = '/commercial61-native-174/bootstrap-runtime087'
    assert source.count(old) == 5
    source = source.replace(old, '/commercial61-native-175/bootstrap-runtime087')
    anchor = '#include "native-usb-storage-174.h"'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '\n#include "usb-readonly-175.h"', 1)
    anchor = '    native_usb148_load();'
    assert source.count(anchor) == 1
    return source.replace(anchor, anchor + '\n    if (native_usb_storage175_guard())return;', 1)


if __name__ == '__main__':
    verified = json.loads((ROOT / 'reports/commercial61-native-173/persistent-offline-verification.json').read_text())
    assert verified['filesystem_clean'] and verified['lab_partition_unmounted']
    source = (BASE / 'build-commercial-native-166.py').read_text()
    source = source.replace('commercial61-native-166', 'commercial61-native-175')
    source = source.replace('ordered_chain_equals_full_166', 'ordered_chain_equals_full_175')
    source = source.replace("sha((BASE/'persistent-data-166.h').read_bytes())", "sha((BASE/'persistent-data-172.h').read_bytes())")
    source = source.replace("sha((BASE/'persistent-runtime-166.h').read_bytes())", "sha((BASE/'persistent-runtime-173.h').read_bytes())")
    anchor = "    metadata['runtime_verified']=False"
    assert source.count(anchor) == 1
    record = "    metadata['usb175']=dict(observer_sha256=sha((BASE/'native-usb-storage-174.h').read_bytes()),guard_sha256=sha((BASE/'usb-readonly-175.h').read_bytes()),media_data_writes_requested=False,new_block_nodes_exposed=False)\n"
    source = source.replace(anchor, record + anchor, 1)
    anchor = "if __name__=='__main__':"
    assert source.count(anchor) == 1
    source = source.replace(anchor, 'runtime166=runtime175\nouter166=outer175\n' + anchor, 1)
    exec(compile(source, 'build-commercial-native-175.generated.py', 'exec'),
         {'__name__':'__main__', '__file__':str(BASE / 'build-commercial-native-175.generated.py'),
          'runtime175':runtime175, 'outer175':outer175})
