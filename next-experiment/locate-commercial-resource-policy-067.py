"""Find the diagnostic owner among libraries actually mapped in preserved logs."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

B = Path(__file__).resolve().parents[1]
OUT = B / 'reports/commercial-resource-policy-locate-067-r3'
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')

if __name__ == '__main__':
    OUT.mkdir(exist_ok=False)
    raw = (B / 'reports/commercial61-native-066/runtime-evidence/raw/interactive-faults030.log').read_bytes()
    paths = set(p.decode().removeprefix('/usr') for p in re.findall(
        rb'(?m)^[0-9a-f]+-[0-9a-f]+ [rwxps-]{4} [0-9a-f]+ [0-9a-f]+:[0-9a-f]+ \d+\s+(/(?:usr/)?system/[^ \r\n]+\.so(?:\.\d+)?)\r?$', raw))
    assert paths and len(paths) < 1500, len(paths)
    priority = ('runtime', 'context', 'ability', 'appkit', 'appspawn', 'resmgr', 'ace')
    paths = sorted(paths, key=lambda p: (not any(k in p for k in priority), p))
    rows = []
    for source in paths:
        blob = subprocess.check_output(['debugfs', '-R', 'cat ' + source, str(IMAGE)], stderr=subprocess.DEVNULL)
        if blob[:4] != b'\x7fELF':
            continue
        matches = [s.decode() for s in (b'CompatiblePolicyDeviceType', b'deviceType is empty') if s in blob]
        rows.append(dict(original_path=source, sha256=hashlib.sha256(blob).hexdigest(), matches=matches))
        if not matches:
            continue
        target = OUT / Path(source).name
        target.open('xb').write(blob)
        for suffix, command in [('symbols', ['aarch64-linux-gnu-nm', '-D', '-C', '--defined-only']),
                                ('disassembly', ['llvm-objdump-19', '-d', '--demangle'])]:
            output = subprocess.check_output(command + [str(target)])
            (OUT / (target.name + '.' + suffix + '.txt')).open('xb').write(output)
        print(json.dumps(rows[-1]))
        break
    result = dict(source_snapshot_sha256=hashlib.sha256(raw).hexdigest(),
                  candidate_count=len(paths), scanned_files=rows,
                  original_image_modified=False, code_executed=False)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print('scanned=', len(rows), 'matched=', any(r['matches'] for r in rows))
