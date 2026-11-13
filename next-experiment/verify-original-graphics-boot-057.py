"""Independent records for actual original-service display initialization failure."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-056.py')))['source']
source = source.replace("def verify(number='056', tag='056', egl=True):", "def verify(number='057', tag='056', egl=True):")
source = source.replace('original-graphics-egl-004', 'original-graphics-egl-005')
anchor = "    collected = BASE / 'reports/baremetal-native-trial-012-collected'"
assert source.count(anchor) == 1
source = source.replace(anchor, "    assert any(row['name'] == 'bridge_error' and row['value'] == '0x3001'\n               and row['pid'] in identities['render_service']['pids'] for row in trace_records)\n" + anchor)
compile(source, 'independent-original-graphics-057', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-057', 'exec'))
