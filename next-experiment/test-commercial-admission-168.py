"""Retest the complete 166 storage admission with the scoped memory-log wrapper."""
from pathlib import Path
import hashlib
import json

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
if __name__=='__main__':
    prior=json.loads((ROOT/'reports/commercial61-native-166-compile-fix-1/result.json').read_text())
    assert hashlib.sha256((BASE/'persistent-runtime-166.h').read_bytes()).hexdigest()==prior['persistent166']['runtime_header_sha256']
    source=(BASE/'test-commercial-admission-166.py').read_text()
    source=source.replace('commercial61-native-166-compile-fix-1','commercial61-native-168')
    source=source.replace('commercial61-native-166','commercial61-native-168')
    source=source.replace('build-commercial-native-166.py','build-commercial-native-168.py')
    source=source.replace("generator['runtime166']","generator['runtime168']").replace("generator['outer166']","generator['outer168']")
    source=source.replace('persistent-runtime-166.h','persistent-runtime-168.h')
    source=source.replace('commercial-workflow-166.py','commercial-workflow-168.py').replace("workflow['source166']","workflow['source168']")
    source=source.replace('estimated166','estimated168')
    source=source.replace("tests=['test-persistent-data-166.py',","tests=['test-persistent-runtime-168.py','test-persistent-data-166.py',",1)
    source=source.replace('fifteen_focused_test_scripts_pass','sixteen_focused_test_scripts_pass')
    exec(compile(source,'test-commercial-admission-168.generated.py','exec'),
        {'__name__':'__main__','__file__':str(BASE/'test-commercial-admission-168.generated.py')})
