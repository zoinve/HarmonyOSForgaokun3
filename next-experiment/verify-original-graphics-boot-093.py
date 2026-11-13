"""Keep independent full-artifact checks; report real AppSpawn query output only."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-092.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS093_STATE ', b'GRAPHICS092_STATE '))


def parse_data_capacity(raw):
    return parent['parse_data_capacity'](raw.replace(b'GRAPHICS093_DATA_CAPACITY ', b'GRAPHICS092_DATA_CAPACITY '))


source = parent['source']
for old, new in [("number='092', tag='092'", "number='093', tag='093'"),
                 ('GRAPHICS092_', 'GRAPHICS093_'),
                 ('baremetal-sdk-original-init-qemu-092', 'baremetal-sdk-original-init-qemu-093'),
                 ('next-experiment/verify-original-graphics-boot-092.py', 'next-experiment/verify-original-graphics-boot-093.py')]:
    assert old in source, old
    source = source.replace(old, new)
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    original_appspawn_log_output = []
    for match in re.finditer(rb'GRAPHICS093_APPSPAWN_QUERY sample=(\d+) pid=(\d+) original_tool=1 tail=200 by_tag=(\d+)\r?\n(.*?)GRAPHICS093_APPSPAWN_QUERY_END sample=\1 pid=\2 status=(-?\d+)', raw, re.S):
        original_appspawn_log_output.append(dict(sample=int(match[1]), pid=int(match[2]),
            by_tag=bool(int(match[3])), wait_status=int(match[5]),
            raw_interleaved_output=match[4].decode('utf-8', errors='replace')))
''' + anchor)
source = source.replace('evidence = dict(', 'evidence = dict(original_appspawn_log_output=original_appspawn_log_output, ')
compile(source, 'independent-original-appspawn-observation-093', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-appspawn-observation-093', 'exec'))
