"""Preservation and actual original-service EGL results, without presuming success."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-060.py')))['source']
source = source.replace("number='060', tag='059'", "number='062', tag='059'")
source = source.replace('original-graphics-egl-007', 'original-graphics-egl-008')
anchor = "    collected = BASE / 'reports/baremetal-native-trial-012-collected'"
assert source.count(anchor) == 1
source = source.replace(anchor, '''    actual_egl_context_created_pids = []
    for pid in identities['render_service']['pids']:
        rows = [row for row in observed_display_stages if row['pid'] == pid]
        def observed(name, nonzero=False):
            return any(row['name'] == name and
                       (int(row['value'], 16) != 0 if nonzero else int(row['value'], 16) == 1)
                       for row in rows)
        if (observed('gbm_device', True) and observed('eglInitialize') and
            observed('eglCreateContext', True)):
            actual_egl_context_created_pids.append(pid)
''' + anchor)
source = source.replace('evidence = dict(', 'evidence = dict(actual_egl_context_created_pids=actual_egl_context_created_pids, ')
compile(source, 'independent-original-graphics-062', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-062', 'exec'))
