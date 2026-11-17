"""Inspect genuine daemon dictionary generation, without executing target code."""
from pathlib import Path
import hashlib
import json
import lzma
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
tools = runpy.run_path(str(BASE / 'audit-commercial-hilog-110.py'))


if __name__ == '__main__':
    out = tools['OUT'] / 'daemon'
    assert not out.exists()
    source = '/system/bin/hilogd'
    process = subprocess.run(['/usr/sbin/debugfs', '-R', 'cat ' + source, tools['IMAGE']], capture_output=True, check=True)
    body = process.stdout
    assert body.startswith(b'\x7fELF')
    out.mkdir()
    elf = out / 'hilogd'
    elf.open('xb').write(body)
    debug = tools['sections'](body).get('.gnu_debugdata')
    assert debug
    mini = out / 'mini.elf'
    mini.open('xb').write(lzma.decompress(debug))
    for name, command in [('symbols', ['aarch64-linux-gnu-nm', '-anC', str(mini)]),
                          ('strings', ['strings', '-a', str(elf)])]:
        (out / (name + '.txt')).open('xb').write(subprocess.check_output(command))
    result = dict(source=source, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
        read_only_debugfs=True, target_code_executed=False, source_image_mounted=False)
    (out / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
