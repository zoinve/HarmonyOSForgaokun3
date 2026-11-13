"""Keep real multicast evidence separate from incomplete serial audit records."""
from pathlib import Path
import re
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-086.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS087_STATE ', b'GRAPHICS086_STATE '))


def parse_profile_events(raw):
    return parent['parse_profile_events'](raw.replace(b'GRAPHICS087_PROFILE_EVENT ', b'GRAPHICS086_PROFILE_EVENT '))


parse_audit_syscalls = parent['parse_audit_syscalls']


def parse_audit_copy(raw):
    rows = parse_audit_syscalls(raw)
    for row in rows:
        paths = []
        for record in row['related_records']:
            match = re.search(r'\bname=(?:"([^"]*)"|([0-9a-fA-F]+)(?=\s|$))', record)
            if not match:
                continue
            if match.group(1) is not None:
                paths.append(match.group(1))
            else:
                try:
                    paths.append(bytes.fromhex(match.group(2)).decode(errors='replace'))
                except ValueError:
                    continue
        row['paths'] = paths
    return rows


source = parent['source']
assert source.count("number='086', tag='086'") == 1
source = source.replace("number='086', tag='086'", "number='087', tag='087'")
source = source.replace('GRAPHICS086_', 'GRAPHICS087_')
source = source.replace('baremetal-sdk-original-init-qemu-086', 'baremetal-sdk-original-init-qemu-087')
source = source.replace('next-experiment/verify-original-graphics-boot-086.py',
                        'next-experiment/verify-original-graphics-boot-087.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    copy_dir = BASE / 'reports/original-audit-copy-087'
    copy_record = json.loads((copy_dir / 'result.json').read_text())
    assert copy_record['original_scratch_unchanged']
    assert not copy_record['original_sdk_images_accessed'] and not copy_record['vm_rerun']
    copy_raw = b''
    if copy_record['log']['present']:
        copy_raw = (copy_dir / 'audit.log').read_bytes()
        assert len(copy_raw) == copy_record['log']['bytes'] <= 64*1024*1024
        assert hashlib.sha256(copy_raw).hexdigest() == copy_record['log']['sha256']
    copy_rows = runpy.run_path(str(BASE / 'next-experiment/verify-original-graphics-boot-087.py'))['parse_audit_copy'](copy_raw)
    samgr_copy_rows = [row for row in copy_rows if row['pid'] in samgr_identity['pids']]
    samgr_copy_profile_rows = [row for row in samgr_copy_rows
        if any(path.endswith('/profile') or '/profile/' in path for path in row['paths'])]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         original_audit_copy_recovery=copy_record,
         original_samgr_audit_copy_syscalls=samgr_copy_rows,
         original_samgr_audit_copy_profile_calls=samgr_copy_profile_rows,
         original_audit_copy_scope='60s/64MiB read-only multicast; no completeness assumption',
         ''')
compile(source, 'independent-original-audit-copy-087', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-audit-copy-087', 'exec'))
