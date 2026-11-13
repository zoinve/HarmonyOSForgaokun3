"""Actual make-current/DAC evidence; never infer service or desktop readiness."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-063.py')))['source']
assert "number='063', tag='063'" in source
source = source.replace("number='063', tag='063'", "number='064', tag='064'")
source = source.replace('original-graphics-egl-008', 'original-graphics-egl-009')
source = source.replace('    observed_display_stages = ',
                        "    stage_names = set(stage_names) | {'eglMakeCurrent'}\n    observed_display_stages = ")
anchor = "    collected = BASE / 'reports/baremetal-native-trial-012-collected'"
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    assert command[command.index('-smp') + 1] == '8'
    assert command[command.index('-m') + 1] == '4096'
    actual_make_current_success_pids = sorted({row['pid'] for row in observed_display_stages
        if row['name'] == 'eglMakeCurrent' and int(row['value'], 16) == 1})
    observed_drm_permissions = [dict(sample=int(sample), path=path.decode(),
        stat=int(rc), uid=int(uid), gid=int(gid), mode=mode.decode())
        for sample, path, rc, uid, gid, mode in re.findall(prefix +
            rb'DRM_PERMISSIONS sample=(\d+) path=(\S+) stat=(-?\d+) uid=(\d+) gid=(\d+) mode=(\d+)', raw)]
    observed_service_group_records = [dict(pid=int(pid), value=value.decode())
        for pid, value in re.findall(prefix + rb'CREDENTIAL pid=(\d+) ((?:Gid|Groups):[^\r\n]*)', raw)]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
        actual_make_current_success_pids=actual_make_current_success_pids,
        observed_drm_permissions=observed_drm_permissions,
        observed_service_group_records=observed_service_group_records,
        ''')
compile(source, 'independent-original-graphics-064', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-064', 'exec'))
