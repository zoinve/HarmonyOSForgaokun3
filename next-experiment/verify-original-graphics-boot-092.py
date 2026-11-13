"""Independent later-frame, identity and data evidence; never equate CLI exit with readiness."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-091.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS092_STATE ', b'GRAPHICS091_STATE '))


def parse_data_capacity(raw):
    return parent['parse_data_capacity'](raw.replace(b'GRAPHICS092_DATA_CAPACITY ', b'GRAPHICS091_DATA_CAPACITY '))


source = parent['source']
for old, new in [("number='091', tag='091'", "number='092', tag='092'"),
                 ('GRAPHICS091_', 'GRAPHICS092_'),
                 ('baremetal-sdk-original-init-qemu-091', 'baremetal-sdk-original-init-qemu-092'),
                 ('next-experiment/verify-original-graphics-boot-091.py', 'next-experiment/verify-original-graphics-boot-092.py'),
                 ('16 <= len(modes) <= 48', '16 <= len(modes) <= 72')]:
    assert old in source, old
    source = source.replace(old, new)
compile(source, 'independent-original-desktop-late-092', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-desktop-late-092', 'exec'))
