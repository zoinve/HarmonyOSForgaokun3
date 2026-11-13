"""Keep full independent checks; distinguish actual mount state from failures."""
from pathlib import Path
import runpy
import re

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-093.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS094_STATE ', b'GRAPHICS093_STATE '))


def parse_data_capacity(raw):
    return parent['parse_data_capacity'](raw.replace(b'GRAPHICS094_DATA_CAPACITY ', b'GRAPHICS093_DATA_CAPACITY '))


def parse_runtime_mounts(raw):
    result = []
    for m in re.finditer(rb'GRAPHICS094_MOUNT_STATE sample=(\d+) path=(/|/mnt) stat=(-?\d+) errno=(\d+) flags=(\d+)', raw):
        ok = int(m[3]) == 0 and int(m[4]) == 0
        result.append(dict(sample=int(m[1]), path=m[2].decode(), stat=int(m[3]), errno=int(m[4]),
                           flags=int(m[5]) if ok else None))
    return result


source = parent['source']
for old, new in [("number='093', tag='093'", "number='094', tag='094'"),
                 ('GRAPHICS093_', 'GRAPHICS094_'),
                 ('baremetal-sdk-original-init-qemu-093', 'baremetal-sdk-original-init-qemu-094'),
                 ('next-experiment/verify-original-graphics-boot-093.py', 'next-experiment/verify-original-graphics-boot-094.py')]:
    assert old in source, old
    source = source.replace(old, new)
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, '''    mount_witness = re.search(rb'GRAPHICS094_MNT_RUNTIME type=1021994 flags=(\\d+) mode=755 uid=0 gid=0 propagation_slave=1 original_early_calls=23500,23520', raw)
    assert mount_witness and int(mount_witness[1]) & 2 and not int(mount_witness[1]) & 1
    observed_runtime_mounts = runpy.run_path(str(BASE/'next-experiment/verify-original-graphics-boot-094.py'))['parse_runtime_mounts'](raw)
''' + anchor)
source = source.replace('evidence = dict(', 'evidence = dict(observed_runtime_mounts=observed_runtime_mounts, ')
compile(source, 'independent-original-runtime-mnt-094', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-runtime-mnt-094', 'exec'))
