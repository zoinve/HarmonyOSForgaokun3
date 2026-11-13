"""Independent actual-pixel checks with an unchanged-guest-byte comparison."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-098.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']
parse_state_records = parent['parse_state_records']
parse_data_capacity = parent['parse_data_capacity']
parse_runtime_mounts = parent['parse_runtime_mounts']
parse_diagnostics = parent['parse_diagnostics']
parse_power_service = parent['parse_power_service']

source = parent['source']
for old, new in [("number='098', tag='098'", "number='099', tag='098'"),
                 ('baremetal-sdk-original-init-qemu-098', 'baremetal-sdk-original-init-qemu-099'),
                 ('next-experiment/verify-original-graphics-boot-098.py', 'next-experiment/verify-original-graphics-boot-099.py')]:
    assert old in source, old
    source = source.replace(old, new)
anchor = "'virtio-gpu-device' in command"
assert source.count(anchor) == 1
source = source.replace(anchor, "'virtio-gpu-device,xres=800,yres=600' in command")
anchor = '    evidence = dict('
assert source.count(anchor) == 1
assert 'baseline =' not in source
source = source.replace(anchor, '''    baseline = json.loads((BASE/'reports/baremetal-sdk-original-init-qemu-098/result.json').read_text())
    assert result['initrd_sha256'] == baseline['initrd_sha256']
    assert 'virtio-gpu-device,xres=800,yres=600' in result['command']
    assert virtual_scanout_verified_frames
    assert all((frame['width'], frame['height']) == (800, 600) for frame in virtual_scanout_verified_frames)
''' + anchor)
source = source.replace('evidence = dict(', 'evidence = dict(unchanged_guest_initrd_verified=True, requested_virtual_display=[800,600], ')
compile(source, 'independent-original-display-load-099', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-display-load-099', 'exec'))
