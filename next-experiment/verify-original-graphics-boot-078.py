"""Preserve original Foundation logs and real responses without assuming a cause."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-077.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS078_STATE ', b'GRAPHICS077_STATE '))


source = parent['source']
assert source.count("number='077', tag='077'") == 1
source = source.replace("number='077', tag='077'", "number='078', tag='078'")
source = source.replace('GRAPHICS077_', 'GRAPHICS078_')
source = source.replace('baremetal-sdk-original-init-qemu-077', 'baremetal-sdk-original-init-qemu-078')
source = source.replace('next-experiment/verify-original-graphics-boot-077.py',
                        'next-experiment/verify-original-graphics-boot-078.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    original_foundation_log_queries = [dict(sample=int(sample), pid=int(pid))
        for sample, pid in re.findall(rb'GRAPHICS078_FOUNDATION_QUERY sample=(\d+) pid=(\d+) original_tool=1 tail=200', raw)]
    original_foundation_log_results = [dict(sample=int(sample), pid=int(pid), wait_status=int(status))
        for sample, pid, status in re.findall(rb'GRAPHICS078_FOUNDATION_QUERY_END sample=(\d+) pid=(\d+) status=(-?\d+)', raw)]
    original_foundation_log_output = [dict(sample=int(sample), pid=int(pid), raw_interleaved_output=text.decode(errors='replace'))
        for sample, pid, text in re.findall(rb'GRAPHICS078_FOUNDATION_QUERY sample=(\d+) pid=(\d+) original_tool=1 tail=200\r?\n(.*?)GRAPHICS078_FOUNDATION_QUERY_END', raw, re.S)]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         original_foundation_log_queries=original_foundation_log_queries,
         original_foundation_log_results=original_foundation_log_results,
         original_foundation_log_output=original_foundation_log_output,
         ''')
compile(source, 'independent-original-desktop-errors-078', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-desktop-errors-078', 'exec'))
