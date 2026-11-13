"""Preserve actual original-tool responses; a start request is not desktop proof."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-076.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS077_STATE ', b'GRAPHICS076_STATE '))


source = parent['source']
assert source.count("number='076', tag='076'") == 1
source = source.replace("number='076', tag='076'", "number='077', tag='077'")
source = source.replace('GRAPHICS076_', 'GRAPHICS077_')
source = source.replace('baremetal-sdk-original-init-qemu-076', 'baremetal-sdk-original-init-qemu-077')
source = source.replace('next-experiment/verify-original-graphics-boot-076.py',
                        'next-experiment/verify-original-graphics-boot-077.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    original_desktop_tool_requests = [dict(sample=int(sample), operation=int(operation))
        for sample, operation in re.findall(rb'GRAPHICS077_DESKTOP_TOOL sample=(\d+) operation=(\d+) original_binary=1 normal_authorization=1', raw)]
    original_desktop_tool_results = [dict(sample=int(sample), operation=int(operation), pid=int(pid), wait_status=int(status))
        for sample, operation, pid, status in re.findall(rb'GRAPHICS077_DESKTOP_TOOL_END sample=(\d+) operation=(\d+) pid=(-?\d+) status=(-?\d+)', raw)]
    original_desktop_tool_output = [dict(sample=int(sample), operation=int(operation), raw_interleaved_output=text.decode(errors='replace'))
        for sample, operation, text in re.findall(rb'GRAPHICS077_DESKTOP_TOOL sample=(\d+) operation=(\d+) original_binary=1 normal_authorization=1\r?\n(.*?)GRAPHICS077_DESKTOP_TOOL_END', raw, re.S)]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         original_desktop_tool_requests=original_desktop_tool_requests,
         original_desktop_tool_results=original_desktop_tool_results,
         original_desktop_tool_output=original_desktop_tool_output,
         ''')
compile(source, 'independent-original-desktop-077', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-desktop-077', 'exec'))
