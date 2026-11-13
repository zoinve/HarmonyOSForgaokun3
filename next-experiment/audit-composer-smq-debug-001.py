"""Read embedded mini-debug ELF symbols; never execute original libraries."""
from pathlib import Path
import hashlib
import json
import lzma
import struct
import subprocess

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'reports/composer-smq-debug-001'


def main():
    assert not OUT.exists(), OUT
    prior = json.loads((BASE / 'reports/composer-smq-001/result.json').read_text())
    OUT.mkdir()
    records = []
    for row in prior['inputs']:
        # POSIX paths must be split explicitly on this Windows host.
        source = Path('//wsl.localhost/Debian' + row['path'])
        body = source.read_bytes()
        assert hashlib.sha256(body).hexdigest() == row['sha256']
        shoff = struct.unpack_from('<Q', body, 40)[0]
        entsize, count, names_index = struct.unpack_from('<HHH', body, 58)
        sections = [struct.unpack_from('<IIQQQQIIQQ', body, shoff + i * entsize)
                    for i in range(count)]
        names = sections[names_index]
        table = body[names[4]:names[4] + names[5]]
        selected = [s for s in sections
                    if table[s[0]:].split(b'\0', 1)[0] == b'.gnu_debugdata']
        assert len(selected) == 1, row['path']
        section = selected[0]
        mini = lzma.decompress(body[section[4]:section[4] + section[5]])
        assert mini[:6] == b'\x7fELF\x02\x01'
        name = row['path'].split('/')[-1]
        target = OUT / (name + '.mini.elf')
        with target.open('xb') as f:
            f.write(mini)
        linux_target = '/mnt/d/lab/HarmonyOSForMatebookego/reports/composer-smq-debug-001/' + target.name
        p = subprocess.run(['wsl', '-d', 'Debian', '--', 'aarch64-linux-gnu-nm',
                            '-anC', linux_target], text=True, capture_output=True, timeout=30)
        assert p.returncode == 0 and not p.stderr, p.stderr
        symbols = OUT / (name + '.symbols.txt')
        with symbols.open('xb') as f:
            f.write(p.stdout.encode())
        records.append(dict(source=row, mini=dict(path=target.name, bytes=len(mini),
            sha256=hashlib.sha256(mini).hexdigest()), symbols=dict(path=symbols.name,
            sha256=hashlib.sha256(symbols.read_bytes()).hexdigest())))
    result = dict(records=records, elf_executed=False, original_libraries_changed=False,
                  matebook_changed=False, serialization_verified=False)
    with (OUT / 'result.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
