"""Preserve complete artifact gates; report actual account and desktop responses."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-083.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']

def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS090_STATE ', b'GRAPHICS083_STATE '))

source = parent['source']
assert source.count("number='083', tag='083'") == 1
source = source.replace("number='083', tag='083'", "number='090', tag='090'")
source = source.replace('GRAPHICS083_', 'GRAPHICS090_')
source = source.replace('baremetal-sdk-original-init-qemu-083', 'baremetal-sdk-original-init-qemu-090')
source = source.replace('next-experiment/verify-original-graphics-boot-083.py',
                        'next-experiment/verify-original-graphics-boot-090.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    assert b'GRAPHICS090_SYSTEM_BIND source=/usr/system target=/system canonical=/system readonly=1 original_files=1' in raw
    original_account_log_results = [dict(sample=int(sample), pid=int(pid), wait_status=int(status))
        for sample, pid, status in re.findall(rb'GRAPHICS090_ACCOUNT_QUERY_END sample=(\d+) pid=(\d+) status=(-?\d+)', raw)]
    original_account_log_output = [dict(sample=int(sample), pid=int(pid), raw_interleaved_output=text.decode(errors='replace'))
        for sample, pid, text in re.findall(rb'GRAPHICS090_ACCOUNT_QUERY sample=(\d+) pid=(\d+) original_tool=1 tail=200\r?\n(.*?)GRAPHICS090_ACCOUNT_QUERY_END', raw, re.S)]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         original_account_log_results=original_account_log_results,
         original_account_log_output=original_account_log_output,
         ''')
compile(source, 'independent-original-account-090', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-account-090', 'exec'))
