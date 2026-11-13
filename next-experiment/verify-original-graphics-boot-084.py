"""Verify immutable artifacts and attribute actual file events to witnessed SAMGR."""
from pathlib import Path
import re
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-083.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS084_STATE ', b'GRAPHICS083_STATE '))


def parse_profile_events(raw):
    return [dict(sequence=int(sequence), pid=int(pid), mask=int(mask, 16),
                 path_raw=path.decode(errors='replace'), link_errno=int(error))
            for sequence, pid, mask, path, error in re.findall(
                rb'GRAPHICS084_PROFILE_EVENT seq=(\d+) pid=(-?\d+) mask=(0x[0-9a-f]+) path=([^\r\n]*?) link_errno=(\d+)', raw)]


source = parent['source']
assert source.count("number='083', tag='083'") == 1
source = source.replace("number='083', tag='083'", "number='084', tag='084'")
source = source.replace('GRAPHICS083_', 'GRAPHICS084_')
source = source.replace('baremetal-sdk-original-init-qemu-083', 'baremetal-sdk-original-init-qemu-084')
source = source.replace('next-experiment/verify-original-graphics-boot-083.py',
                        'next-experiment/verify-original-graphics-boot-084.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    samgr_pids = runpy.run_path(str(BASE / 'next-experiment/original-graphics-process-records-001.py'))['extract_process_pids'](raw, prefix, 'samgr')
    samgr_identity = runpy.run_path(str(BASE / 'next-experiment/original-graphics-identity-records-001.py'))['audit_identities'](raw, prefix, samgr_pids, 5555, 'samgr')
    profile_events = runpy.run_path(str(BASE / 'next-experiment/verify-original-graphics-boot-084.py'))['parse_profile_events'](raw)
    samgr_profile_events = [event for event in profile_events if event['pid'] in samgr_identity['pids']]
    samgr_installs_events = [event for event in samgr_profile_events
        if event['link_errno'] == 0 and event['path_raw'].endswith('/profile/installs.json')]
    profile_watch_lines = [line.decode(errors='replace') for line in raw.splitlines()
        if b'GRAPHICS084_PROFILE_WATCH_' in line]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         original_profile_watch_lines=profile_watch_lines,
         original_profile_events=profile_events,
         samgr_identity=samgr_identity,
         samgr_profile_events=samgr_profile_events,
         samgr_installs_file_open_observed=any(event['mask'] & 0x20 for event in samgr_installs_events),
         samgr_installs_file_access_observed=any(event['mask'] & 0x01 for event in samgr_installs_events),
         ''')
compile(source, 'independent-original-profile-events-084', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-profile-events-084', 'exec'))
