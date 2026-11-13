"""Verify EGL integration evidence while retaining the guest critical-fault failure."""
from pathlib import Path

source = Path(__file__).with_name('verify-original-graphics-boot-053.py').read_text()
source = source.replace("def verify(number='053', tag='050', egl=False):",
                        "def verify(number='054', tag='054', egl=True):")
source = source.replace("assert result['observation_timed_out'] and result['qemu_returncode'] is None",
                        "assert not result['observation_timed_out'] and result['qemu_returncode'] == 0\n"
                        "    assert b'reboot: Restarting system' in raw\n"
                        "    assert b'ProcessCriticalProcessFault serviceName is foundation' in raw")
source = source.replace("for name in ['libdisplay_composer_vdi_impl.z.so', 'libdisplay_buffer_vdi_impl.z.so']:",
                        "for name in ['libdisplay_composer_vdi_impl.z.so']:")
source = source.replace('reference_vdis_mapped=True,',
                        "reference_vdis_mapped=False, allocator_vdi_mapping_observed=bool(re.search(prefix + rb'MAP pid=\\d+ [^\\r\\n]*/vendor/lib64/libdisplay_buffer_vdi_impl.z.so', raw)),")
anchor = "    collected = BASE / 'reports/baremetal-native-trial-012-collected'"
assert source.count(anchor) == 1
source = source.replace(anchor, '''    mapped_rs = []
    for pid in identities['render_service']['pids']:
        required = ['/system/lib64/libEGL_impl.so',
                    '/system/lib64/harmony-mesa/libEGL.so.1',
                    '/system/lib64/harmony-mesa/libgallium-25.0.1.so',
                    '/system/lib64/harmony-mesa/libc++_shared.so',
                    '/system/lib64/chipset-sdk-sp/libc++.so']
        if all(re.search(prefix + ('MAP pid=%d ' % pid).encode() + rb'[^\\r\\n]*' + re.escape(path.encode()), raw) for path in required):
            mapped_rs.append(pid)
    assert mapped_rs, 'Actual original RenderService bridge/Mesa/platform mappings missing'
''' + anchor)
source = source.replace("evidence = dict(serial_sha256=", "evidence = dict(reference_egl_mesa_mapped_in_original_render_service=mapped_rs, serial_sha256=")
compile(source, 'independent-original-graphics-054', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-054', 'exec'))
