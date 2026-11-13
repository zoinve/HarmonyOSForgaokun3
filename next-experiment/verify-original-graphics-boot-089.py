"""Retain all original artifact/identity/pixel checks; do not assume SA recovery."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-088.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']
parse_audit_syscalls = parent['parse_audit_syscalls']
parse_audit_copy = parent['parse_audit_copy']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS089_STATE ', b'GRAPHICS088_STATE '))


def parse_profile_events(raw):
    return parent['parse_profile_events'](raw.replace(b'GRAPHICS089_PROFILE_EVENT ', b'GRAPHICS088_PROFILE_EVENT '))


source = parent['source']
assert source.count("number='088', tag='088'") == 1
source = source.replace("number='088', tag='088'", "number='089', tag='089'")
source = source.replace('GRAPHICS088_', 'GRAPHICS089_')
source = source.replace('original-init-qemu-088', 'original-init-qemu-089')
source = source.replace('original-audit-copy-088', 'original-audit-copy-089')
source = source.replace('next-experiment/verify-original-graphics-boot-088.py',
                        'next-experiment/verify-original-graphics-boot-089.py')
compile(source, 'independent-original-system-bind-089', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-system-bind-089', 'exec'))
