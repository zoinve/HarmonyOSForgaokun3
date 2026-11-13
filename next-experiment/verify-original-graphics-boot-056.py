"""Independently verify real load witnesses, not GPU initialization success."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-055.py')))['source']
source = source.replace("def verify(number='055', tag='055', egl=True):", "def verify(number='056', tag='056', egl=True):")
source = source.replace('original-graphics-egl-003', 'original-graphics-egl-004')
anchor = "    collected = BASE / 'reports/baremetal-native-trial-012-collected'"
assert source.count(anchor) == 1
source = source.replace(anchor, '''    assert prefix + b'TRACE_DIR sample=0 stat=0' in raw
    assert any(row['name'] == 'bridge_loaded' and row['pid'] in identities['render_service']['pids']
               and row['value'] == '0x3eb' for row in trace_records)
''' + anchor)
compile(source, 'independent-original-graphics-056', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-056', 'exec'))
