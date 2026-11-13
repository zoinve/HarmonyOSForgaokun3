"""Keep original artifact/pixel checks and explicitly report command errors."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-078.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS079_STATE ', b'GRAPHICS078_STATE '))


source = parent['source']
assert source.count("number='078', tag='078'") == 1
source = source.replace("number='078', tag='078'", "number='079', tag='079'")
source = source.replace('GRAPHICS078_', 'GRAPHICS079_')
source = source.replace('baremetal-sdk-original-init-qemu-078', 'baremetal-sdk-original-init-qemu-079')
source = source.replace('next-experiment/verify-original-graphics-boot-078.py',
                        'next-experiment/verify-original-graphics-boot-079.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, '''    foundation_query_command_errors = [row for row in original_foundation_log_output
        if "commands can't be used in combination" in row['raw_interleaved_output']]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         foundation_query_command_errors=foundation_query_command_errors,
         ''')
compile(source, 'independent-original-foundation-tail-079', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-foundation-tail-079', 'exec'))
