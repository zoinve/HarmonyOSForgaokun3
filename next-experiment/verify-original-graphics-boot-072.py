"""Verify actual all-PID state and bounded task reads, including access failures."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-071.py')))


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS072_STATE ', b'GRAPHICS071_STATE '))


source = parent['source']
assert source.count("number='071', tag='071'") == 1
source = source.replace("number='071', tag='071'", "number='072', tag='072'")
source = source.replace('GRAPHICS071_', 'GRAPHICS072_')
source = source.replace('next-experiment/verify-original-graphics-boot-071.py',
                        'next-experiment/verify-original-graphics-boot-072.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    observed_original_process_roles = [dict(sample=int(sample), pid=int(pid), parent_pid=int(ppid))
        for sample, pid, ppid in re.findall(rb'GRAPHICS072_ROLE sample=(\d+) pid=(\d+) PPid:\s*(\d+)', raw)]
    observed_original_thread_state = [dict(sample=int(sample), pid=int(pid), tid=int(tid),
        kind=kind.decode(), bytes=int(size), errno=int(error), data=data.decode(errors='replace'))
        for sample, pid, tid, kind, size, error, data in re.findall(
        rb'GRAPHICS072_THREAD sample=(\d+) pid=(\d+) tid=(\d+) kind=(wchan|syscall) bytes=(-?\d+) errno=(\d+) data=([^\r\n]*)', raw)]
    actual_original_rs_thread_state = [row for row in observed_original_thread_state if row['pid'] in verified_rs_pids]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         observed_original_process_roles=observed_original_process_roles,
         observed_original_thread_state=observed_original_thread_state,
         actual_original_rs_thread_state=actual_original_rs_thread_state,
         ''')
compile(source, 'independent-original-roles-072', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-roles-072', 'exec'))
