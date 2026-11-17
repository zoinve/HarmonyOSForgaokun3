"""Inspect only the supplied commercial image's genuine logging decoder."""
from pathlib import Path
import hashlib
import json
import lzma
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMAGE = '/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img'
OUT = ROOT / 'reports/commercial-hilog-audit-110'
CANDIDATES = ['/system/bin/hilog', '/system/lib64/libhilog_inner.so',
              '/system/lib64/libhilog.so', '/system/lib64/chipset-sdk-sp/libhilog.so']


def sections(data):
    assert data[:6] == b'\x7fELF\x02\x01'
    offset = struct.unpack_from('<Q', data, 40)[0]
    size, count, index = struct.unpack_from('<HHH', data, 58)
    assert size == 64 and offset + size * count <= len(data)
    table = [struct.unpack_from('<IIQQQQIIQQ', data, offset + i * size) for i in range(count)]
    entry = table[index]
    names = data[entry[4]:entry[4] + entry[5]]
    return {names[s[0]:].split(b'\0', 1)[0].decode(): data[s[4]:s[4] + s[5]]
            for s in table if s[1] != 8}


if __name__ == '__main__':
    assert not OUT.exists()
    OUT.mkdir()
    files, missing = [], []
    for index, source in enumerate(CANDIDATES):
        process = subprocess.run(['/usr/sbin/debugfs', '-R', 'cat ' + source, IMAGE], capture_output=True, check=True)
        if not process.stdout.startswith(b'\x7fELF'):
            assert b'File not found' in process.stderr, process.stderr
            missing.append(source)
            continue
        data = process.stdout
        prefix = str(index) + '-' + Path(source).name
        library = OUT / prefix
        library.open('xb').write(data)
        commands = [('strings', ['strings', '-a', str(library)]),
                    ('dynamic', ['aarch64-linux-gnu-readelf', '-dW', str(library)]),
                    ('symbols', ['aarch64-linux-gnu-nm', '-DC', str(library)])]
        debug = sections(data).get('.gnu_debugdata')
        if debug:
            mini = OUT / (prefix + '.mini.elf')
            mini.open('xb').write(lzma.decompress(debug))
            commands.append(('mini-symbols', ['aarch64-linux-gnu-nm', '-anC', str(mini)]))
        for suffix, command in commands:
            result = subprocess.run(command, capture_output=True, check=True)
            (OUT / (prefix + '.' + suffix + '.txt')).open('xb').write(result.stdout)
        files.append(dict(source=source, local=prefix, bytes=len(data),
            sha256=hashlib.sha256(data).hexdigest(), mini_symbols_present=bool(debug)))
    assert any(item['source'] == '/system/bin/hilog' for item in files)
    result = dict(files=files, absent_candidates=missing, read_only_debugfs=True,
        source_image_mounted=False, original_binary_modified=False, target_boot_performed=False,
        decoded_early_messages_recovered=False)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
