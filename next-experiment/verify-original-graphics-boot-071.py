"""Preserve original evidence; distinguish failed reads from real null fields."""
from pathlib import Path
import re
import runpy


def parse_state_records(raw):
    pattern = (rb'GRAPHICS071_STATE sample=(\d+) pid=(\d+) field=([a-z_]+) '
               rb'bytes=(-?\d+) errno=(\d+) (?:base=0x([0-9a-f]+) value=0x([0-9a-f]+)|mapped=0) '
               rb'private_hash_specific_state=1')
    rows = []
    for sample, pid, field, size, error, base, value in re.findall(pattern, raw):
        name = field.decode()
        width = 1 if name.endswith('_guard') else 8
        success = int(size) == width and int(error) == 0 and bool(base)
        rows.append(dict(sample=int(sample), pid=int(pid), field=name,
                         bytes=int(size), errno=int(error), read_success=success,
                         base=int(base, 16) if base else None,
                         value=int(value, 16) if success else None))
    return rows


source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-070.py')))['source']
assert source.count("number='070', tag='070'") == 1
source = source.replace("number='070', tag='070'", "number='071', tag='071'")
source = source.replace('GRAPHICS070_', 'GRAPHICS071_')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, '''    parse_states = runpy.run_path(str(BASE / 'next-experiment/verify-original-graphics-boot-071.py'))['parse_state_records']
    observed_original_state = parse_states(raw)
    verified_rs_pids = identities['render_service']['pids']
    actual_original_rs_state = [row for row in observed_original_state if row['pid'] in verified_rs_pids]
    assert json.loads((BASE / 'reports/original-composer-client-001/result.json').read_text())['rs_elf_sha256'] == 'c031105598312ed0d074ccf0742f985b22c701c905cac1bb679746112c582d6d'
    assert json.loads((BASE / 'reports/original-render-fault-054/result.json').read_text())['rs_elf_sha256'] == 'fce31219aad17f8fa8a4dcd910284caa030fc0cf081e30037c8c730b5d53a633'
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         observed_original_state=observed_original_state,
         actual_original_rs_state=actual_original_rs_state,
         private_hash_specific_state_only=True,
         target_memory_modified=False,
         ''')
compile(source, 'independent-original-state-071', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-state-071', 'exec'))
