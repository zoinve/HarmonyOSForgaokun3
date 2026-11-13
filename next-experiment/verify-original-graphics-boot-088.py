"""Measure original SAMGR/profile and business outcomes without assuming a fix."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-087.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']
parse_audit_syscalls = parent['parse_audit_syscalls']
parse_audit_copy = parent['parse_audit_copy']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS088_STATE ', b'GRAPHICS087_STATE '))


def parse_profile_events(raw):
    return parent['parse_profile_events'](raw.replace(b'GRAPHICS088_PROFILE_EVENT ', b'GRAPHICS087_PROFILE_EVENT '))


source = parent['source']
assert source.count("number='087', tag='087'") == 1
source = source.replace("number='087', tag='087'", "number='088', tag='088'")
source = source.replace('GRAPHICS087_', 'GRAPHICS088_')
source = source.replace('original-init-qemu-087', 'original-init-qemu-088')
source = source.replace('original-audit-copy-087', 'original-audit-copy-088')
source = source.replace('next-experiment/verify-original-graphics-boot-087.py',
                        'next-experiment/verify-original-graphics-boot-088.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    assert b'GRAPHICS088_SYSTEM_BIND source=/usr/system target=/system canonical=/system readonly=1 original_files=1' in raw
''' + anchor)
compile(source, 'independent-original-system-bind-088', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-system-bind-088', 'exec'))
