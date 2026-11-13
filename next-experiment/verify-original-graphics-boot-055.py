"""Verify captured real EGL calls, not a presumed graphics fix or desktop."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-054.py')))['source']
source = source.replace("def verify(number='054', tag='054', egl=True):",
                        "def verify(number='055', tag='055', egl=True):")
anchor = "    assert not result['observation_timed_out'] and result['qemu_returncode'] == 0\n    assert b'reboot: Restarting system' in raw\n    assert b'ProcessCriticalProcessFault serviceName is foundation' in raw"
assert source.count(anchor) == 1
source = source.replace(anchor, "    assert (result['observation_timed_out'] and result['qemu_returncode'] is None) or (not result['observation_timed_out'] and result['qemu_returncode'] == 0)")
source = source.replace('original-graphics-egl-002', 'original-graphics-egl-003')
anchor = "    for name in ['libdisplay_composer_vdi_impl.z.so']:\n        assert re.search(prefix + rb'MAP pid=\\d+ [^\\r\\n]*/vendor/lib64/' + name.encode(), raw)"
assert source.count(anchor) == 1
source = source.replace(anchor, "    composer_vdi_mapping_observed = bool(re.search(prefix + rb'MAP pid=\\d+ [^\\r\\n]*/vendor/lib64/libdisplay_composer_vdi_impl.z.so', raw))")
anchor = "    collected = BASE / 'reports/baremetal-native-trial-012-collected'"
assert source.count(anchor) == 1
source = source.replace(anchor, r'''
    traces = sorted(set(re.findall(rb'EGL_TRACE pid=(\d+) name=([^\s]+) value=(0x[0-9a-f]+) errno=(-?\d+)', raw)))
    trace_records = [dict(pid=int(pid), name=name.decode(), value=value.decode(), errno=int(error))
                     for pid, name, value, error in traces]
    if trace_records:
        assert any(row['pid'] in identities['render_service']['pids'] for row in trace_records)
''' + anchor)
source = source.replace('evidence = dict(reference_egl_mesa_mapped_in_original_render_service=',
                        'evidence = dict(composer_vdi_mapping_observed=composer_vdi_mapping_observed, egl_trace_capture_observed=bool(trace_records), real_egl_trace_records=trace_records, reference_egl_mesa_mapped_in_original_render_service=')
compile(source, 'independent-original-graphics-055', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-055', 'exec'))
