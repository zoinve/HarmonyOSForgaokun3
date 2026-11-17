"""Decode original SceneBoard OOBE lifecycle methods without changing images."""
from pathlib import Path
import hashlib
import importlib.util
import io
import json
import runpy
import struct
import subprocess
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
OUT = ROOT / 'reports/sceneboard-oobe-audit-097'


def main():
    assert not OUT.exists(), 'Preserve numbered evidence'
    decoder = runpy.run_path(str(ROOT / 'next-experiment/decode-commercial-oobe-methods-079.py'))
    isa = (ROOT / 'reports/commercial-oobe-flow-audit-079/openharmony-isa-1e0c629.yaml').read_bytes()
    assert hashlib.sha256(isa).hexdigest() == decoder['ISA_SHA']
    table = decoder['instruction_table'](yaml.safe_load(isa))
    spec = importlib.util.spec_from_file_location('abc_index', ROOT / 'references/L410-Linux-Compatibility-Platform/abc_record_index.py')
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    read = subprocess.run(['debugfs', '-R', 'cat /system/app/SceneBoard/SceneBoard.hap', str(IMAGE)], capture_output=True, check=True)
    hap = read.stdout
    assert len(hap) == 87269511
    assert hashlib.sha256(hap).hexdigest() == 'f36168b19efc69b6a3246f557ddadd8e0534e5c208c093b6a00e94917391da80'
    with zipfile.ZipFile(io.BytesIO(hap)) as archive:
        data = archive.read('ets/modules.abc')
    header = parser.HEADER.unpack_from(data)
    regions = [struct.unpack_from('<10I', data, header[13] + i * 40) for i in range(header[12])]
    decoded, records, strings = [], [], {}
    for i in range(header[6]):
        offset = struct.unpack_from('<I', data, header[7] + i * 4)[0]
        record = parser.parse_record_prefix(data, offset, len(data))
        if 'oobe' not in record['name'].lower():
            continue
        fields, methods = parser.parse_record_members(data, record, len(data))
        records.append(dict(record=record, fields=fields, methods=methods))
        for method in methods:
            if method.get('code_off') is None:
                continue
            region = next(r for r in regions if r[0] <= method['offset'] < r[1])
            if region not in strings:
                ids = struct.unpack_from('<' + str(region[4]) + 'I', data, region[5])
                strings[region] = [parser.read_string_item(data, at, len(data)) for at in ids]
            code = data[method['insn_off']:method['insn_off'] + method['code_size']]
            method['instruction_sha256'] = hashlib.sha256(code).hexdigest()
            decoded.append(dict(record=record['name'], method=method,
                                instructions=decoder['decode'](code, table, strings[region])))
    assert any('BaseOobeManager' in r['record']['name'] for r in records)
    assert decoded
    OUT.mkdir()
    result = dict(hap_sha256=hashlib.sha256(hap).hexdigest(), abc_sha256=hashlib.sha256(data).hexdigest(),
                  isa_sha256=decoder['ISA_SHA'], records=records, methods=decoded,
                  original_modified=False, operational_boot_performed=False,
                  module_import_names_unresolved=True, exception_control_flow_unresolved=True,
                  all_decoded_branches_on_instruction_boundaries=True)
    with (OUT / 'decoded-methods.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    with (OUT / 'decoded-methods.txt').open('x') as stream:
        for entry in decoded:
            stream.write('\n' + entry['record'] + '\n' + entry['method']['name'] + '\n')
            for insn in entry['instructions']:
                args = ', '.join(str(o.get('string', o['value'])) for o in insn['operands'])
                target = ' -> ' + str(insn['target']) if 'target' in insn else ''
                stream.write(f"{insn['offset']:04d} {insn['name']} {args}{target}\n")
    print(json.dumps(dict(records=len(records), methods=len(decoded),
                         instructions=sum(len(m['instructions']) for m in decoded),
                         original_modified=False, operational_boot_performed=False)))


if __name__ == '__main__':
    main()
