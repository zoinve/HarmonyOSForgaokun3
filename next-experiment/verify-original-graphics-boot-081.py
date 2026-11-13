"""Retain genuine SAMGR errors/visible files and independent artifact checks."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-080.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS081_STATE ', b'GRAPHICS080_STATE '))


source = parent['source']
assert source.count("number='080', tag='080'") == 1
source = source.replace("number='080', tag='080'", "number='081', tag='081'")
source = source.replace('GRAPHICS080_', 'GRAPHICS081_')
source = source.replace('baremetal-sdk-original-init-qemu-080', 'baremetal-sdk-original-init-qemu-081')
source = source.replace('next-experiment/verify-original-graphics-boot-080.py',
                        'next-experiment/verify-original-graphics-boot-081.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    original_samgr_log_results = [dict(sample=int(sample), pid=int(pid), wait_status=int(status))
        for sample, pid, status in re.findall(rb'GRAPHICS081_SAMGR_QUERY_END sample=(\d+) pid=(\d+) status=(-?\d+)', raw)]
    original_samgr_log_output = [dict(sample=int(sample), pid=int(pid), raw_interleaved_output=text.decode(errors='replace'))
        for sample, pid, text in re.findall(rb'GRAPHICS081_SAMGR_QUERY sample=(\d+) pid=(\d+) original_tool=1 head=600\r?\n(.*?)GRAPHICS081_SAMGR_QUERY_END', raw, re.S)]
    original_samgr_profile_output = [dict(sample=int(sample), pid=int(pid), root=root.decode(), bytes=int(count), errno=int(error), raw_interleaved_output=text.decode(errors='replace'))
        for sample, pid, root, count, error, text in re.findall(rb'GRAPHICS081_SAMGR_PROFILE sample=(\d+) pid=(\d+) root=(\w+) bytes=(-?\d+) errno=(\d+)\r?\n(.*?)GRAPHICS081_SAMGR_PROFILE_END', raw, re.S)]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         original_samgr_log_results=original_samgr_log_results,
         original_samgr_log_output=original_samgr_log_output,
         original_samgr_profile_output=original_samgr_profile_output,
         ''')
compile(source, 'independent-original-samgr-profile-081', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-samgr-profile-081', 'exec'))
