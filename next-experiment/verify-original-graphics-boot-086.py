"""Preserve real audit return codes; no missing-event or permission assumptions."""
from pathlib import Path
import re
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-085.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS086_STATE ', b'GRAPHICS085_STATE '))


def parse_profile_events(raw):
    return parent['parse_profile_events'](raw.replace(b'GRAPHICS086_PROFILE_EVENT ', b'GRAPHICS085_PROFILE_EVENT '))


def parse_audit_syscalls(raw):
    grouped = {}
    for line in raw.splitlines():
        # Console writes can concatenate records. Preserve raw logs, but never
        # combine one event's serial/path with a later event's UID or result.
        if len(re.findall(rb'audit\([0-9.]+:\d+\):', line)) != 1:
            continue
        match = re.search(rb'\btype=(\d+|[A-Z_]+).*?audit\(([0-9.]+:\d+)\):\s*(.*)', line)
        if match:
            kind, serial, body = match.groups()
            grouped.setdefault(serial, []).append((kind, body, line))
    rows = []
    for serial, records in grouped.items():
        for kind, body, line in records:
            if kind not in (b'1300', b'SYSCALL'):
                continue
            pairs = re.findall(rb'\b(arch|syscall|exit|pid|uid|success)=([^\s]+)', body)
            if len({key for key, _ in pairs}) != len(pairs):
                continue
            fields = dict(pairs)
            if fields.get(b'uid') != b'5555' or fields.get(b'arch') != b'c00000b7':
                continue
            if not all(key in fields for key in (b'syscall', b'exit', b'pid')):
                continue
            try:
                row = dict(audit_id=serial.decode(), pid=int(fields[b'pid']), uid=5555,
                           syscall=int(fields[b'syscall']), exit=int(fields[b'exit']),
                           success_raw=fields.get(b'success', b'').decode(errors='replace'),
                           raw=line.decode(errors='replace'),
                           related_records=[other.decode(errors='replace') for other_kind, _, other in records
                                            if other_kind not in (b'1300', b'SYSCALL')])
            except ValueError:
                continue
            rows.append(row)
    return rows


source = parent['source']
assert source.count("number='085', tag='085'") == 1
source = source.replace("number='085', tag='085'", "number='086', tag='086'")
source = source.replace('GRAPHICS085_', 'GRAPHICS086_')
source = source.replace('baremetal-sdk-original-init-qemu-085', 'baremetal-sdk-original-init-qemu-086')
source = source.replace('next-experiment/verify-original-graphics-boot-085.py',
                        'next-experiment/verify-original-graphics-boot-086.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    audit_syscalls = runpy.run_path(str(BASE / 'next-experiment/verify-original-graphics-boot-086.py'))['parse_audit_syscalls'](raw)
    samgr_audit_syscalls = [row for row in audit_syscalls if row['pid'] in samgr_identity['pids']]
    audit_setup = [line.decode(errors='replace') for line in raw.splitlines()
        if b'GRAPHICS086_AUDIT_' in line]
    audit_loss_lines = [line.decode(errors='replace') for line in raw.splitlines()
        if any(word in line for word in (b'audit_lost=', b'audit_backlog=', b'kauditd_printk_skb:', b'backlog limit exceeded', b'rate limit exceeded'))]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         original_audit_setup=audit_setup,
         original_uid5555_audit_syscalls=audit_syscalls,
         original_samgr_audit_syscalls=samgr_audit_syscalls,
         original_audit_loss_lines=audit_loss_lines,
         ''')
compile(source, 'independent-original-audit-086', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-audit-086', 'exec'))
