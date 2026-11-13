"""Verify preservation and report actual display stages, not presumed success."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-056.py')))['source']
source = source.replace("number='056', tag='056'", "number='059', tag='059'")
source = source.replace('original-graphics-egl-004', 'original-graphics-egl-006')
anchor = "    collected = BASE / 'reports/baremetal-native-trial-012-collected'"
assert source.count(anchor) == 1
source = source.replace(anchor, '''    assert prefix + b'GBM_BACKEND_PATH' in raw
    stage_names = {'drm_open_result', 'gbm_device', 'mesa_display', 'eglInitialize',
                   'eglBindAPI', 'eglChooseConfig', 'eglCreateContext',
                   'eglCreatePbufferSurface', 'eglMakeCurrent', 'bridge_error'}
    observed_display_stages = [row for row in trace_records
                               if row['pid'] in identities['render_service']['pids']
                               and row['name'] in stage_names]
''' + anchor)
source = source.replace('evidence = dict(', 'evidence = dict(observed_display_stages=observed_display_stages, ')
compile(source, 'independent-original-graphics-059', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-059', 'exec'))
