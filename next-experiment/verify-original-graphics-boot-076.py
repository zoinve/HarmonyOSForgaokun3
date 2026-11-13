"""Independently preserve frames and report actual Commit returns/process presence."""
from pathlib import Path
import re
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-075.py')))
inspect_frame = parent['inspect_frame']
parse_parent_state = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-074.py')))['parse_state_records']


def parse_state_records(raw):
    return parse_parent_state(raw.replace(b'GRAPHICS076_STATE ', b'GRAPHICS074_STATE '))


def decode_commit_result(stage):
    match = re.fullmatch(r'Commit_rc_(neg_)?(\d+)', stage)
    if not match:
        return None
    return int(match[2]) * (-1 if match[1] else 1)


source = parent['source']
assert source.count("number='075', tag='074'") == 1
source = source.replace("number='075', tag='074'", "number='076', tag='076'")
source = source.replace('GRAPHICS074_', 'GRAPHICS076_')
source = source.replace('original-graphics-provider-004', 'original-graphics-provider-005')
source = source.replace('baremetal-sdk-original-init-qemu-075', 'baremetal-sdk-original-init-qemu-076')
source = source.replace('next-experiment/verify-original-graphics-boot-075.py',
                        'next-experiment/verify-original-graphics-boot-076.py')
source = source.replace('next-experiment/verify-original-graphics-boot-074.py',
                        'next-experiment/verify-original-graphics-boot-076.py')
old = "assert result['initrd_sha256']==json.loads((project/'reports/baremetal-sdk-original-init-qemu-074/result.json').read_text())['initrd_sha256']\n"
assert source.count(old) == 1
source = source.replace(old, '')  # New observer/provider; still independently hash-check actual archive.
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    decode_result = runpy.run_path(str(BASE / 'next-experiment/verify-original-graphics-boot-076.py'))['decode_commit_result']
    actual_commit_return_records = [dict(pid=row['pid'], uid=row['uid'], result=decode_result(row['stage']))
        for row in actual_original_composer_trace if decode_result(row['stage']) is not None]
    observed_all_processes = [dict(sample=int(sample), pid=int(pid), cmd=cmd.decode(errors='replace'))
        for sample, pid, cmd in re.findall(rb'GRAPHICS076_ALL_PROCESS sample=(\d+) pid=(\d+) cmd=([^\r\n]*)', raw)]
    observed_all_process_identities = [dict(sample=int(sample), pid=int(pid), uids=[int(value) for value in values.split()])
        for sample, pid, values in re.findall(rb'GRAPHICS076_ALL_IDENTITY sample=(\d+) pid=(\d+) Uid:\s*((?:\d+[\t ]+){3}\d+)', raw)]
    observed_all_process_domains = [dict(sample=int(sample), pid=int(pid), domain=domain.decode())
        for sample, pid, domain in re.findall(rb'GRAPHICS076_ALL_DOMAIN sample=(\d+) pid=(\d+) value=(u:[A-Za-z0-9_:]+)', raw)]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         actual_commit_return_records=actual_commit_return_records,
         observed_all_processes=observed_all_processes,
         observed_all_process_identities=observed_all_process_identities,
         observed_all_process_domains=observed_all_process_domains,
         ''')
compile(source, 'independent-original-content-076', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-content-076', 'exec'))
