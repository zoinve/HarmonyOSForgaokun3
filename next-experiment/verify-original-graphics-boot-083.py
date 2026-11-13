"""Report real query output, retaining all original artifact and identity gates."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-082.py')))
inspect_frame = parent['inspect_frame']
decode_commit_result = parent['decode_commit_result']

def parse_state_records(raw):
    return parent['parse_state_records'](raw.replace(b'GRAPHICS083_STATE ', b'GRAPHICS082_STATE '))

source = parent['source']
assert source.count("number='082', tag='082'") == 1
source = source.replace("number='082', tag='082'", "number='083', tag='083'")
source = source.replace('GRAPHICS082_', 'GRAPHICS083_')
source = source.replace('baremetal-sdk-original-init-qemu-082', 'baremetal-sdk-original-init-qemu-083')
source = source.replace('next-experiment/verify-original-graphics-boot-082.py',
                        'next-experiment/verify-original-graphics-boot-083.py')
anchor = "module_body=entries['graphics-ashmem.ko'][1]"
assert source.count(anchor) == 1
source = source.replace(anchor, '''query=json.loads((project/'reports/original-config-query-001/result.json').read_text())
query_body=entries['graphics-config-query'][1]
assert len(query_body)==query['bytes'] and hashlib.sha256(query_body).hexdigest()==query['sha256']
''' + anchor)
source = source.replace('ashmem_module_archive_verified=True,',
                        'ashmem_module_archive_verified=True,config_query_archive_verified=True,')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    original_config_query_results = [dict(sample=int(sample), wait_status=int(status))
        for sample, status in re.findall(rb'GRAPHICS083_CONFIG_QUERY_END sample=(\d+) status=(-?\d+)', raw)]
    original_config_query_output = [dict(sample=int(sample), raw_interleaved_output=text.decode(errors='replace'))
        for sample, text in re.findall(rb'GRAPHICS083_CONFIG_QUERY sample=(\d+) diagnostic_caller_not_samgr=1\r?\n(.*?)GRAPHICS083_CONFIG_QUERY_END', raw, re.S)]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         original_config_query_results=original_config_query_results,
         original_config_query_output=original_config_query_output,
         ''')
compile(source, 'independent-original-config-query-083', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-config-query-083', 'exec'))
