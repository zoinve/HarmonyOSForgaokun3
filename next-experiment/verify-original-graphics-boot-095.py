"""Independently preserve all artifacts; report actual SceneBoard log output."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-094.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS095_STATE ', b'GRAPHICS094_STATE '))


def parse_data_capacity(raw):
    return parent['parse_data_capacity'](raw.replace(b'GRAPHICS095_DATA_CAPACITY ', b'GRAPHICS094_DATA_CAPACITY '))


def parse_runtime_mounts(raw):
    return parent['parse_runtime_mounts'](raw.replace(b'GRAPHICS095_MOUNT_STATE ', b'GRAPHICS094_MOUNT_STATE '))


source = parent['source']
for old, new in [("number='094', tag='094'", "number='095', tag='095'"),
                 ('GRAPHICS094_', 'GRAPHICS095_'),
                 ('baremetal-sdk-original-init-qemu-094', 'baremetal-sdk-original-init-qemu-095'),
                 ('next-experiment/verify-original-graphics-boot-094.py', 'next-experiment/verify-original-graphics-boot-095.py')]:
    assert old in source, old
    source = source.replace(old, new)
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    original_sceneboard_log_output = []
    for match in re.finditer(rb'GRAPHICS095_SCENEBOARD_QUERY sample=(\d+) pid=(\d+) original_tool=1 tail=400\r?\n(.*?)GRAPHICS095_SCENEBOARD_QUERY_END sample=\1 pid=\2 status=(-?\d+)', raw, re.S):
        original_sceneboard_log_output.append(dict(sample=int(match[1]), pid=int(match[2]),
            wait_status=int(match[4]), raw_interleaved_output=match[3].decode('utf-8', errors='replace')))
''' + anchor)
source = source.replace('evidence = dict(', 'evidence = dict(original_sceneboard_log_output=original_sceneboard_log_output, ')
compile(source, 'independent-original-sceneboard-logs-095', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-sceneboard-logs-095', 'exec'))
