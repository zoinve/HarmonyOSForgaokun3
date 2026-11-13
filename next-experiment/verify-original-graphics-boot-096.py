"""Keep full independent evidence checks; report genuine later application logs."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-095.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS096_STATE ', b'GRAPHICS095_STATE '))


def parse_data_capacity(raw):
    return parent['parse_data_capacity'](raw.replace(b'GRAPHICS096_DATA_CAPACITY ', b'GRAPHICS095_DATA_CAPACITY '))


def parse_runtime_mounts(raw):
    return parent['parse_runtime_mounts'](raw.replace(b'GRAPHICS096_MOUNT_STATE ', b'GRAPHICS095_MOUNT_STATE '))


source = parent['source']
for old, new in [("number='095', tag='095'", "number='096', tag='096'"),
                 ('GRAPHICS095_', 'GRAPHICS096_'),
                 ('baremetal-sdk-original-init-qemu-095', 'baremetal-sdk-original-init-qemu-096'),
                 ('next-experiment/verify-original-graphics-boot-095.py', 'next-experiment/verify-original-graphics-boot-096.py')]:
    assert old in source, old
    source = source.replace(old, new)
compile(source, 'independent-original-sceneboard-late-096', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-sceneboard-late-096', 'exec'))
