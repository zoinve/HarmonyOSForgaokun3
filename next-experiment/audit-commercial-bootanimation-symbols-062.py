"""Recover embedded original mini-debug symbols without changing the binary."""
from pathlib import Path
import hashlib
import json
import lzma
import struct
import subprocess

BASE = Path(__file__).resolve().parents[1]
AUDIT = BASE / 'reports/commercial-bootanimation-audit-062'
OUT = BASE / 'reports/commercial-bootanimation-symbols-062-r2'


def main():
    assert not OUT.exists(), 'Preserve numbered evidence'
    binary = AUDIT / 'bootanimation'
    data = binary.read_bytes()
    assert hashlib.sha256(data).hexdigest() == '51e312f723a36af50907e48cbe6cd191da021fdaeca6a3d2d43b4badf1eaf84a'
    header = struct.unpack_from('<16sHHIQQQIHHHHHH', data)
    sections = [struct.unpack_from('<IIQQQQIIQQ', data, header[6] + i * header[11])
                for i in range(header[12])]
    names_section = sections[header[13]]
    names = data[names_section[4]:names_section[4] + names_section[5]]
    debug = [s for s in sections if names[s[0]:].split(b'\0', 1)[0] == b'.gnu_debugdata']
    assert len(debug) == 1
    section = debug[0]
    mini = lzma.decompress(data[section[4]:section[4] + section[5]])
    assert mini.startswith(b'\x7fELF')
    OUT.mkdir()
    mini_path = OUT / 'mini-debug.elf'
    mini_path.open('xb').write(mini)
    symbols = subprocess.check_output(['aarch64-linux-gnu-nm', '-C', '-S', '--defined-only', str(mini_path)], text=True)
    (OUT / 'symbols.txt').open('x').write(symbols)
    selected = []
    for line in symbols.splitlines():
        fields = line.split(maxsplit=3)
        if len(fields) != 4 or fields[2] not in ('t', 'T'):
            continue
        address, size, _, name = fields
        if name == 'main' or any(k in name for k in ['BootAnimationController',
                'BootAnimation::', 'BootCompatibleDisplayStrategy', '~Boot', 'StopBootAnimation']):
            va, length = int(address, 16), int(size, 16)
            if not length:
                continue
            asm = subprocess.check_output(['llvm-objdump-19', '-d', '--demangle',
                '--start-address=' + hex(va), '--stop-address=' + hex(va + length), str(binary)], text=True)
            filename = hex(va) + '.asm'
            target = OUT / filename
            if target.exists():
                assert target.read_text() == asm, 'Aliased symbols must have identical code'
            else:
                target.open('x').write(asm)
            selected.append(dict(symbol=name, virtual_address=hex(va), size=length, assembly=filename))
    result = dict(original_sha256=hashlib.sha256(data).hexdigest(),
                  embedded_debug_sha256=hashlib.sha256(mini).hexdigest(),
                  methods=selected, original_binary_modified=False,
                  runtime_execution_not_proven=True)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
