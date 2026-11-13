"""Keep full original image/pixel checks and retain real BMS startup failures."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-079.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS080_STATE ', b'GRAPHICS079_STATE '))


source = parent['source']
assert source.count("number='079', tag='079'") == 1
source = source.replace("number='079', tag='079'", "number='080', tag='080'")
source = source.replace('GRAPHICS079_', 'GRAPHICS080_')
source = source.replace('baremetal-sdk-original-init-qemu-079', 'baremetal-sdk-original-init-qemu-080')
source = source.replace('next-experiment/verify-original-graphics-boot-079.py',
                        'next-experiment/verify-original-graphics-boot-080.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, '''    original_bms_startup_lines = [line
        for row in original_foundation_log_output
        for line in row['raw_interleaved_output'].splitlines()
        if any(word.lower() in line.lower() for word in
            ('Installd', 'CreateBmsServiceDir', 'LoadSystemAbility', 'Mkdir',
             '/foundation/BMS:', 'bmsdb.db'))]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         original_bms_startup_lines=original_bms_startup_lines,
         ''')
compile(source, 'independent-original-bms-head-080', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-bms-head-080', 'exec'))
