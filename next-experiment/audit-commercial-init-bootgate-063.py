"""Read-only original init boot-event symbols and code, without executing init."""
from pathlib import Path
import hashlib
import json
import lzma
import struct
import subprocess

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'reports/commercial-init-bootgate-audit-063'
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')


def main():
    assert not OUT.exists(), 'Preserve numbered evidence'
    data = subprocess.check_output(['debugfs', '-R', 'cat /system/bin/init', str(IMAGE)], stderr=subprocess.DEVNULL)
    assert data.startswith(b'\x7fELF\x02\x01')
    OUT.mkdir()
    binary = OUT / 'original-init'
    binary.open('xb').write(data)
    for name, command in [('dynamic-symbols.txt', ['aarch64-linux-gnu-nm', '-D', '-C']),
                          ('strings.txt', ['strings', '-t', 'x']),
                          ('all.asm', ['llvm-objdump-19', '-d', '--demangle'])]:
        text = subprocess.check_output(command + [str(binary)], text=True)
        (OUT / name).open('x').write(text)
    header = struct.unpack_from('<16sHHIQQQIHHHHHH', data)
    sections = [struct.unpack_from('<IIQQQQIIQQ', data, header[6] + i * header[11])
                for i in range(header[12])]
    strings_section = sections[header[13]]
    names = data[strings_section[4]:strings_section[4] + strings_section[5]]
    debug = [s for s in sections if names[s[0]:].split(b'\0', 1)[0] == b'.gnu_debugdata']
    selected = []
    if debug:
        assert len(debug) == 1
        section = debug[0]
        mini = lzma.decompress(data[section[4]:section[4] + section[5]])
        mini_path = OUT / 'mini-debug.elf'
        mini_path.open('xb').write(mini)
        symbols = subprocess.check_output(['aarch64-linux-gnu-nm', '-C', '-S', '--defined-only', str(mini_path)], text=True)
        (OUT / 'mini-symbols.txt').open('x').write(symbols)
        for line in symbols.splitlines():
            fields = line.split(maxsplit=3)
            if len(fields) != 4 or fields[2] not in ('t', 'T'):
                continue
            address, size, _, name = fields
            if not any(word in name.lower() for word in ['bootevent', 'bootcompleted']):
                continue
            va, length = int(address, 16), int(size, 16)
            if not length:
                continue
            filename = hex(va) + '.asm'
            asm = subprocess.check_output(['llvm-objdump-19', '-d', '--demangle',
                '--start-address=' + hex(va), '--stop-address=' + hex(va + length), str(binary)], text=True)
            target = OUT / filename
            if target.exists():
                assert target.read_text() == asm
            else:
                target.open('x').write(asm)
            selected.append(dict(symbol=name, virtual_address=hex(va), size=length, assembly=filename))
    result = dict(origin='/system/bin/init', image=str(IMAGE), bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(), embedded_debug_present=bool(debug),
        methods=selected, images_modified=False, original_init_executed=False,
        boot_flags_modified=False, runtime_bootgate_state_not_observed=True)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
