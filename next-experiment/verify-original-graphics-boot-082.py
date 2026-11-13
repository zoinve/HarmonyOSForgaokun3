"""Retain actual parameter output/errors and all independent preservation gates."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-081.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']


def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS082_STATE ', b'GRAPHICS081_STATE '))


source = parent['source']
assert source.count("number='081', tag='081'") == 1
source = source.replace("number='081', tag='081'", "number='082', tag='082'")
source = source.replace('GRAPHICS081_', 'GRAPHICS082_')
source = source.replace('baremetal-sdk-original-init-qemu-081', 'baremetal-sdk-original-init-qemu-082')
source = source.replace('next-experiment/verify-original-graphics-boot-081.py',
                        'next-experiment/verify-original-graphics-boot-082.py')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    original_config_parameter_results = [dict(sample=int(sample), key=key.decode(), wait_status=int(status))
        for sample, key, status in re.findall(rb'GRAPHICS082_CONFIG_PARAM_END sample=(\d+) key=([\w.]+) status=(-?\d+)', raw)]
    original_config_parameter_output = [dict(sample=int(sample), key=key.decode(), raw_interleaved_output=text.decode(errors='replace'))
        for sample, key, text in re.findall(rb'GRAPHICS082_CONFIG_PARAM sample=(\d+) key=([\w.]+) original_tool=1 read_only=1\r?\n(.*?)GRAPHICS082_CONFIG_PARAM_END', raw, re.S)]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         original_config_parameter_results=original_config_parameter_results,
         original_config_parameter_output=original_config_parameter_output,
         ''')
compile(source, 'independent-original-config-policy-082', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-config-policy-082', 'exec'))
