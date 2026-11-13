"""Keep independent image/pixel checks and actual power-service query responses."""
from pathlib import Path
import runpy
import re

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-097.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS098_STATE ', b'GRAPHICS097_STATE '))


def parse_data_capacity(raw):
    return parent['parse_data_capacity'](raw.replace(b'GRAPHICS098_DATA_CAPACITY ', b'GRAPHICS097_DATA_CAPACITY '))


def parse_runtime_mounts(raw):
    return parent['parse_runtime_mounts'](raw.replace(b'GRAPHICS098_MOUNT_STATE ', b'GRAPHICS097_MOUNT_STATE '))


def parse_diagnostics(raw):
    return parent['parse_diagnostics'](raw.replace(b'GRAPHICS098_', b'GRAPHICS097_'))


def parse_power_service(raw):
    result = []
    for m in re.finditer(rb'GRAPHICS098_POWER_SERVICE_QUERY sample=(\d+) pid=(\d+) original_tool=1 tail=400\r?\n(.*?)GRAPHICS098_POWER_SERVICE_QUERY_END sample=\1 pid=\2 status=(-?\d+)', raw, re.S):
        result.append(dict(sample=int(m[1]), pid=int(m[2]), wait_status=int(m[4]),
                           raw_interleaved_output=m[3].decode('utf-8', errors='replace')))
    return result


source = parent['source']
for old, new in [("number='097', tag='097'", "number='098', tag='098'"),
                 ('GRAPHICS097_', 'GRAPHICS098_'),
                 ('baremetal-sdk-original-init-qemu-097', 'baremetal-sdk-original-init-qemu-098'),
                 ('next-experiment/verify-original-graphics-boot-097.py', 'next-experiment/verify-original-graphics-boot-098.py')]:
    assert old in source, old
    source = source.replace(old, new)
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, '''    power_service_logs = runpy.run_path(str(BASE/'next-experiment/verify-original-graphics-boot-098.py'))['parse_power_service'](raw)
''' + anchor)
source = source.replace('evidence = dict(', 'evidence = dict(original_power_service_log_output=power_service_logs, ')
compile(source, 'independent-original-power-service-098', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-power-service-098', 'exec'))
