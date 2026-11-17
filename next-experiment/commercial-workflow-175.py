"""Single protected USB diagnostic; all original boot preservation guards remain."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-175-compile-fix-1'
PREVIOUS = runpy.run_path(str(BASE / 'commercial-workflow-174.py'))
configure_local_transport = PREVIOUS['configure_local_transport']
OPERATIONS = PREVIOUS['OPERATIONS']


def source175(operation):
    source = PREVIOUS['source174'](operation)
    source = source.replace('commercial61-native-174', 'commercial61-native-175')
    source = source.replace('commercial-return-audit-174', 'commercial-return-audit-175')
    source = source.replace('ordered_chain_equals_full_174', 'ordered_chain_equals_full_175')
    source = source.replace('estimated174', 'estimated175')
    source = source.replace("/'reports/commercial61-native-175'", "/'reports/commercial61-native-175-compile-fix-1'")
    source = source.replace('/home/zoinve/harmony-virgl-883/commercial61-native-175/',
                            '/home/zoinve/harmony-virgl-883/commercial61-native-175-compile-fix-1/')
    source = source.replace('native read-only USB storage visibility diagnostic 174',
                            'native protected USB storage visibility diagnostic 175')
    if operation == 'install-commercial-native':
        anchor = ' harmony.persistent_data166=1'
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + ' harmony.usb_readonly175=1', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in [*OPERATIONS, 'retain-entries']
    assert all(json.loads((REPORT / 'admission-test.json').read_text()).values())
    configure_local_transport()
    if sys.argv[1] == 'retain-entries':
        runpy.run_path(str(BASE / 'retain-latest-experiment-boot-entries-001.py'), run_name='__main__')
    else:
        operation = sys.argv[1]
        source = source175(operation)
        assert source == (REPORT / (operation + '.generated.py')).read_text()
        exec(compile(source, operation, 'exec'), {'__name__':'__main__', '__file__':str(BASE / (operation + '-175.py'))})
