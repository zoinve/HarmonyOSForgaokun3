"""Preserve the existing disk data and archive the additional pre-init diagnostic log."""
from pathlib import Path
import json
import runpy

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
generator=runpy.run_path(str(BASE/'build-commercial-native-166.py'))

def runtime168(source):
    return generator['runtime166'](source).replace('persistent-runtime-166.h','persistent-runtime-168.h').replace(
        'persistent_runtime166();','persistent_runtime168();')

def outer168(source,digest,filesystem_uuid):
    return generator['outer166'](source,digest,filesystem_uuid).replace(
        '/commercial61-native-166/bootstrap-runtime087','/commercial61-native-168/bootstrap-runtime087')

if __name__=='__main__':
    check=json.loads((ROOT/'reports/commercial61-native-167/persistent-offline-verification.json').read_text())
    assert check['filesystem_clean'] and check['disk_marker_matches_native_runtime']
    source=(BASE/'build-commercial-native-166.py').read_text()
    source=source.replace('commercial61-native-166','commercial61-native-168')
    source=source.replace("'-166/'","'-168/'")
    source=source.replace('persistent-runtime-166.h','persistent-runtime-168.h')
    source=source.replace('persistent_runtime166();','persistent_runtime168();')
    source=source.replace('ordered_chain_equals_full_166','ordered_chain_equals_full_168')
    exec(compile(source,'build-commercial-native-168.generated.py','exec'),
        {'__name__':'__main__','__file__':str(BASE/'build-commercial-native-168.generated.py')})
