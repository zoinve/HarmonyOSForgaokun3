from pathlib import Path
import json

BASE = Path(__file__).resolve().parents[1]


def instrument(source):
    audit = json.loads((BASE / 'reports/commercial-trace-audit-046/result.json').read_text())
    assert audit['original_elf_hashes_verified'] and audit['executable_offsets_verified']
    names = ['request', 'register_agent', 'recv_parcel', 'on_vsync']
    rows = {row['event']: row for row in audit['probes']}
    specs = []
    for name in names:
        row = rows[name]
        specs.append('{' + ','.join([json.dumps(name), json.dumps(row['library']), row['file_offset'] + 'ULL', hex(int.from_bytes(bytes.fromhex(row['original_instruction']), 'little')) + 'u']) + '}')
    helper = (BASE / 'next-experiment/commercial-hwbreak-050.h').read_text()
    assert helper.count('HW050_SPECS') == 1
    helper = helper.replace('HW050_SPECS', ',\n'.join(specs))
    anchor = 'static void native_original(void)'
    assert source.count(anchor) == 1
    source = source.replace(anchor, helper + '\n' + anchor, 1)
    anchor = 'native_diagnostics(child);snapshot();if(got==child)break;sleep(5);'
    assert source.count(anchor) == 1
    source = source.replace(anchor, 'native_diagnostics(child);hw050_tick(child,0);snapshot();if(got==child)break;sleep(5);', 1)
    anchor = 'commercial_outer_binder044(child);snapshot();'
    assert source.count(anchor) == 1
    source = source.replace(anchor, 'commercial_outer_binder044(child);hw050_tick(child,0);snapshot();', 1)
    anchor = '            if(got==0){'
    assert source.count(anchor) == 1
    return source.replace(anchor, '            hw050_tick(child,1);\n' + anchor, 1)
