"""Read-only original InternetManager decoding with pinned ISA and ABC hashes."""
from pathlib import Path
import hashlib
import importlib.util
import json
import runpy
import struct
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    decoder = runpy.run_path(str(Path(__file__).with_name('decode-commercial-oobe-methods-079.py')))
    isa = (ROOT / 'reports/commercial-oobe-flow-audit-079/openharmony-isa-1e0c629.yaml').read_bytes()
    assert hashlib.sha256(isa).hexdigest() == decoder['ISA_SHA']
    table = decoder['instruction_table'](yaml.safe_load(isa))
    spec = importlib.util.spec_from_file_location('abc_index', ROOT / 'references/L410-Linux-Compatibility-Platform/abc_record_index.py')
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    hap = ROOT / 'reports/commercial-ui-resources-audit-068/HwStartupGuide.hap'
    assert hashlib.sha256(hap.read_bytes()).hexdigest() == '392566ac1deefe9a269db3ebe45513038ed773f210e628f0ca55ce73ed34a1a7'
    with zipfile.ZipFile(hap) as archive:
        data = archive.read('ets/modules.abc')
    assert hashlib.sha256(data).hexdigest() == '28318c1036a7fe23ddfbacf012d6f4d071854a54dfa320f8a322b55eacbb4ef7'
    header = parser.HEADER.unpack_from(data)
    regions = [struct.unpack_from('<10I', data, header[13] + i * 40) for i in range(header[12])]
    decoded = []
    for i in range(header[6]):
        offset = struct.unpack_from('<I', data, header[7] + i * 4)[0]
        record = parser.parse_record_prefix(data, offset, len(data))
        if not record['name'].endswith('/InternetManager;'):
            continue
        fields, methods = parser.parse_record_members(data, record, len(data))
        for method in methods:
            if method.get('code_off') is None:
                continue
            region = next(r for r in regions if r[0] <= method['offset'] < r[1])
            ids = struct.unpack_from('<' + str(region[4]) + 'I', data, region[5])
            strings = [parser.read_string_item(data, at, len(data)) for at in ids]
            code = data[method['insn_off']:method['insn_off'] + method['code_size']]
            method['instruction_sha256'] = hashlib.sha256(code).hexdigest()
            decoded.append(dict(record=record['name'], method=method, instructions=decoder['decode'](code, table, strings)))
    assert decoded
    folder = ROOT / 'reports/commercial-oobe-network-audit-085'
    folder.mkdir(exist_ok=False)
    result = dict(abc_sha256=hashlib.sha256(data).hexdigest(), isa_sha256=decoder['ISA_SHA'],
                  methods=decoded, all_decoded_branches_on_instruction_boundaries=True,
                  original_modified=False, module_import_names_unresolved=True,
                  private_binary_patched=False, operational_boot_performed=False)
    with (folder / 'decoded-methods.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    with (folder / 'decoded-methods.txt').open('x') as stream:
        for entry in decoded:
            stream.write('\n' + entry['record'] + '\n' + entry['method']['name'] + '\n')
            for insn in entry['instructions']:
                args = ', '.join(str(o.get('string', o['value'])) for o in insn['operands'])
                target = ' -> ' + str(insn['target']) if 'target' in insn else ''
                stream.write(f"{insn['offset']:04d} {insn['name']} {args}{target}\n")
    print(json.dumps(dict(methods=len(decoded), instructions=sum(len(m['instructions']) for m in decoded))))


if __name__ == '__main__':
    main()
