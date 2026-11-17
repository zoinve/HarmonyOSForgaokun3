"""Compare module structure sections in the preserved and rebuilt ELF files."""
from pathlib import Path
import hashlib
import json
import struct

BASE = Path(__file__).resolve().parents[1]
ROOT = Path('/home/zoinve/harmony-virgl-883')
OUT = BASE / 'reports/native-trace-kernel-047/module-abi-audit.json'


def module_size(path):
    data = path.read_bytes()
    header = struct.unpack_from('<16sHHIQQQIHHHHHH', data)
    assert header[0][:6] == b'\x7fELF\x02\x01' and header[2] == 183
    offset, step, count, strings = header[6], header[11], header[12], header[13]
    assert step == 64 and 0 < strings < count
    sections = [struct.unpack_from('<IIQQQQIIQQ', data, offset + i * step)
                for i in range(count)]
    names = sections[strings]
    table = data[names[4]:names[4] + names[5]]
    matches = [s[5] for s in sections
               if table[s[0]:].split(b'\0', 1)[0] == b'.gnu.linkonce.this_module']
    assert len(matches) == 1
    return dict(path=str(path), bytes=matches[0], sha256=hashlib.sha256(data).hexdigest())


def main():
    assert not OUT.exists(), 'Preserve evidence'
    result = json.loads((OUT.parent / 'result.json').read_text())
    assert result['previous_unchanged'] and result['configuration_unchanged']
    rows = []
    for relative in ['drivers/nvme/host/nvme.ko', 'drivers/phy/qualcomm/phy-qcom-qmp-pcie.ko']:
        old = module_size(ROOT / 'native-trace-kernel-046/out' / relative)
        new = module_size(ROOT / 'native-trace-kernel-047/out' / relative)
        rows.append(dict(module=relative, old=old, rebuilt=new,
                         structure_size_changed=old['bytes'] != new['bytes']))
    assert all(row['structure_size_changed'] for row in rows)
    report = dict(rows=rows, old_module_abi_incompatible=True,
                  runtime_failure_cause_proven=False, force_loading_used=False)
    with OUT.open('x') as stream:
        json.dump(report, stream, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
