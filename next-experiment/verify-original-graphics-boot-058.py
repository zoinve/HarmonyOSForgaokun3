"""Verify the observed GBM failure, not a presumed fix."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-057.py')))['source']
source = source.replace("def verify(number='057', tag='056', egl=True):", "def verify(number='058', tag='056', egl=True):")
source = source.replace('original-graphics-egl-005', 'original-graphics-egl-006')
anchor = "    collected = BASE / 'reports/baremetal-native-trial-012-collected'"
assert source.count(anchor) == 1
source = source.replace(anchor, "    for name in ['drm_open_result', 'gbm_device']:\n        assert any(row['name'] == name and row['value'] == '0x0'\n                   and row['pid'] in identities['render_service']['pids'] for row in trace_records)\n" + anchor)
compile(source, 'independent-original-graphics-058', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-058', 'exec'))
