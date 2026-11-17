"""Read-only method index of the unchanged original OOBE ABC."""
from pathlib import Path
import hashlib
import importlib.util
import json
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    spec = importlib.util.spec_from_file_location('abc_index', ROOT / 'references/L410-Linux-Compatibility-Platform/abc_record_index.py')
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    source = ROOT / 'reports/commercial-ui-resources-audit-068/HwStartupGuide.hap'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == '392566ac1deefe9a269db3ebe45513038ed773f210e628f0ca55ce73ed34a1a7'
    with zipfile.ZipFile(source) as archive:
        data = archive.read('ets/modules.abc')
    assert hashlib.sha256(data).hexdigest() == '28318c1036a7fe23ddfbacf012d6f4d071854a54dfa320f8a322b55eacbb4ef7'
    header = parser.HEADER.unpack_from(data)
    assert header[0] == parser.MAGIC and header[3] == len(data)
    count, index = header[6:8]
    assert index + count * 4 <= len(data)
    matches, errors = [], []
    needles = ('quicksetup', 'activation', 'finishoobe', 'oobemanager', 'experience')
    for i in range(count):
        offset = struct.unpack_from('<I', data, index + i * 4)[0]
        record = parser.parse_record_prefix(data, offset, len(data))
        try:
            fields, methods = parser.parse_record_members(data, record, len(data))
        except (ValueError, IndexError, struct.error) as exc:
            errors.append(dict(record=record['name'], error=str(exc)))
            continue
        if any(n in record['name'].lower() for n in needles) or any(any(n in m['name'].lower() for n in needles) for m in methods):
            for method in methods:
                if method.get('code_off') is not None:
                    start = method['insn_off']
                    end = start + method['code_size']
                    assert 0 <= start <= end <= len(data)
                    method['instruction_sha256'] = hashlib.sha256(data[start:end]).hexdigest()
            matches.append(dict(record=record, fields=fields, methods=methods))
    result = dict(abc_sha256=hashlib.sha256(data).hexdigest(), version=list(header[2]), total_records=count, matched_records=matches, parse_errors=errors, original_modified=False, operational_boot_performed=False, instruction_decoding_performed=False, names_do_not_establish_control_flow=True)
    output = ROOT / 'reports/commercial-oobe-flow-audit-079/method-index.json'
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(dict(output=str(output), matched=len(matches), errors=len(errors))))


if __name__ == '__main__':
    main()
