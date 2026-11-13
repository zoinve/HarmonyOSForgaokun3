"""Independently check immutable artifacts/pixels; keep real diagnostic responses."""
from pathlib import Path
import runpy
import re

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-096.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS097_STATE ', b'GRAPHICS096_STATE '))


def parse_data_capacity(raw):
    return parent['parse_data_capacity'](raw.replace(b'GRAPHICS097_DATA_CAPACITY ', b'GRAPHICS096_DATA_CAPACITY '))


def parse_runtime_mounts(raw):
    return parent['parse_runtime_mounts'](raw.replace(b'GRAPHICS097_MOUNT_STATE ', b'GRAPHICS096_MOUNT_STATE '))


def parse_diagnostics(raw):
    rs, power = [], []
    for m in re.finditer(rb'GRAPHICS097_RS_QUERY sample=(\d+) pid=(\d+) original_tool=1 tail=400\r?\n(.*?)GRAPHICS097_RS_QUERY_END sample=\1 pid=\2 status=(-?\d+)', raw, re.S):
        rs.append(dict(sample=int(m[1]), pid=int(m[2]), wait_status=int(m[4]),
                       raw_interleaved_output=m[3].decode('utf-8', errors='replace')))
    for m in re.finditer(rb'GRAPHICS097_POWER_QUERY sample=(\d+) key=([a-z.]+) original_tool=1 read_only=1\r?\n(.*?)GRAPHICS097_POWER_QUERY_END sample=\1 key=\2 status=(-?\d+)', raw, re.S):
        power.append(dict(sample=int(m[1]), key=m[2].decode(), wait_status=int(m[4]),
                          raw_interleaved_output=m[3].decode('utf-8', errors='replace')))
    return dict(render_service=rs, power_parameters=power)


source = parent['source']
for old, new in [("number='096', tag='096'", "number='097', tag='097'"),
                 ('GRAPHICS096_', 'GRAPHICS097_'),
                 ('baremetal-sdk-original-init-qemu-096', 'baremetal-sdk-original-init-qemu-097'),
                 ('next-experiment/verify-original-graphics-boot-096.py', 'next-experiment/verify-original-graphics-boot-097.py')]:
    assert old in source, old
    source = source.replace(old, new)
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, '''    diagnostics = runpy.run_path(str(BASE/'next-experiment/verify-original-graphics-boot-097.py'))['parse_diagnostics'](raw)
''' + anchor)
source = source.replace('evidence = dict(', 'evidence = dict(original_render_service_log_output=diagnostics["render_service"], original_power_parameter_output=diagnostics["power_parameters"], ')
compile(source, 'independent-original-rs-diagnostics-097', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-rs-diagnostics-097', 'exec'))
