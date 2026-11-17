"""Decode original OOBE instructions using pinned upstream ISA; never patch."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import struct
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/commercial-oobe-flow-audit-079'
ISA_SHA = 'b8b69da3b2a458c0dd21e788d52fc1c95ee0619a2510145ea80784c59e4c2918'
PREFIXES = {'throw': 0xfe, 'wide': 0xfd, 'deprecated': 0xfc, 'callruntime': 0xfb}


def instruction_table(document):
    table = {}
    for group in document['groups']:
        for insn in group['instructions']:
            prefix = PREFIXES.get(insn.get('prefix'))
            for opcode, fmt in zip(insn['opcode_idx'], insn['format'], strict=True):
                key = (prefix, opcode)
                assert key not in table
                properties = list(group.get('properties', [])) + list(insn.get('properties', []))
                if 'string_id' in insn['sig']:
                    properties.append('string_id')
                table[key] = dict(name=insn['sig'].split()[0], format=fmt,
                                  properties=properties)
    return table


def decode(code, table, strings):
    result, cursor = [], 0
    while cursor < len(code):
        first = code[cursor]
        prefix_size = 2 if first in PREFIXES.values() else 1
        assert cursor + prefix_size <= len(code), 'truncated opcode'
        key = (first, code[cursor + 1]) if prefix_size == 2 else (None, first)
        meta = table[key]
        fields = re.findall(r'([a-zA-Z0-9]+)_(\d+)', meta['format'])
        bit_cursor, operands = prefix_size * 8, []
        total_bits = bit_cursor + sum(int(width) for _, width in fields)
        assert total_bits % 8 == 0, 'non-byte instruction size'
        size = total_bits // 8
        assert cursor + size <= len(code), 'truncated operands'
        raw = code[cursor:cursor + size]
        packed = int.from_bytes(raw, 'little')
        for name, width in fields:
            width = int(width)
            value = (packed >> bit_cursor) & ((1 << width) - 1)
            operand = dict(name=name, bits=width, value=value)
            if name == 'id' and 'string_id' in meta['properties']:
                assert value < len(strings), 'string index out of bounds'
                operand['string'] = strings[value]
            operands.append(operand)
            bit_cursor += width
        item = dict(offset=cursor, name=meta['name'], raw=raw.hex(), operands=operands)
        if meta['name'].startswith('j'):
            immediate = next(o for o in operands if o['name'].startswith('imm'))
            value, width = immediate['value'], immediate['bits']
            relative = value - (1 << width) if value & (1 << (width - 1)) else value
            item['target'] = cursor + relative
        result.append(item)
        cursor += size
    boundaries = {i['offset'] for i in result}
    for item in result:
        if 'target' in item:
            assert item['target'] in boundaries, ('invalid branch target', item)
    return result


def main():
    isa = (OUT / 'openharmony-isa-1e0c629.yaml').read_bytes()
    assert hashlib.sha256(isa).hexdigest() == ISA_SHA
    table = instruction_table(yaml.safe_load(isa))
    spec = importlib.util.spec_from_file_location('abc_index', ROOT / 'references/L410-Linux-Compatibility-Platform/abc_record_index.py')
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    with zipfile.ZipFile(ROOT / 'reports/commercial-ui-resources-audit-068/HwStartupGuide.hap') as archive:
        data = archive.read('ets/modules.abc')
    assert hashlib.sha256(data).hexdigest() == '28318c1036a7fe23ddfbacf012d6f4d071854a54dfa320f8a322b55eacbb4ef7'
    header = parser.HEADER.unpack_from(data)
    regions = [struct.unpack_from('<10I', data, header[13] + i * 40) for i in range(header[12])]
    index = json.loads((OUT / 'method-index.json').read_text())
    selected = ('GuideHomeAbility;', '/OOBEUtil;', '/QuickSetupViewDataMgr;',
                '/DeviceActivationTaskManager;', '/DeviceActivationPageController;',
                '/PsiActivationTask;', '/MdmActivationTask;',
                '/QuickSetupPageController;', '/BasePageOrderController;')
    decoded = []
    for record in index['matched_records']:
        if not record['record']['name'].endswith(selected):
            continue
        for method in record['methods']:
            if method.get('code_off') is None:
                continue
            region = next(r for r in regions if r[0] <= method['offset'] < r[1])
            ids = struct.unpack_from('<' + str(region[4]) + 'I', data, region[5])
            strings = [parser.read_string_item(data, offset, len(data)) for offset in ids]
            start = method['insn_off']
            code = data[start:start + method['code_size']]
            assert hashlib.sha256(code).hexdigest() == method['instruction_sha256']
            decoded.append(dict(record=record['record']['name'], method=method,
                                instructions=decode(code, table, strings)))
    result = dict(isa_commit='1e0c6290df7bf1ad858bcddf116dfbb24286b895', isa_sha256=ISA_SHA,
                  abc_sha256=hashlib.sha256(data).hexdigest(), methods=decoded,
                  all_decoded_branches_on_instruction_boundaries=True,
                  original_modified=False, operational_boot_performed=False,
                  module_import_names_unresolved=True)
    with (OUT / 'decoded-methods-revision2.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    with (OUT / 'decoded-methods-revision2.txt').open('x') as stream:
        for entry in decoded:
            stream.write('\n' + entry['record'] + '\n' + entry['method']['name'] + '\n')
            for insn in entry['instructions']:
                args = ', '.join(str(o.get('string', o['value'])) for o in insn['operands'])
                target = ' -> ' + str(insn['target']) if 'target' in insn else ''
                stream.write(f"{insn['offset']:04d} {insn['name']} {args}{target}\n")
    print(json.dumps(dict(methods=len(decoded), instructions=sum(len(m['instructions']) for m in decoded))))


if __name__ == '__main__':
    main()
