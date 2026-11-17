"""Locate resource-policy diagnostics in original libraries without running them."""
from pathlib import Path
import hashlib
import json
import subprocess

B = Path(__file__).resolve().parents[1]
OUT = B / 'reports/commercial-resource-policy-audit-067'
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
NAMES = ('libappkit_native.z.so', 'libabilitykit_native.z.so')

if __name__ == '__main__':
    OUT.mkdir(exist_ok=False)
    records = []
    for name in NAMES:
        source = '/system/lib64/platformsdk/' + name
        blob = subprocess.check_output(['debugfs', '-R', 'cat ' + source, str(IMAGE)], stderr=subprocess.DEVNULL)
        assert blob[:6] == b'\x7fELF\x02\x01', source
        target = OUT / name
        target.open('xb').write(blob)
        symbols = subprocess.check_output(['aarch64-linux-gnu-nm', '-D', '-C', '--defined-only', str(target)])
        (OUT / (name + '.symbols.txt')).open('xb').write(symbols)
        found = b'CompatiblePolicyDeviceType' in blob or b'deviceType is empty' in blob
        if found:
            assembly = subprocess.check_output(['llvm-objdump-19', '-d', '--demangle', str(target)])
            (OUT / (name + '.disassembly.txt')).open('xb').write(assembly)
        records.append(dict(original_path=source, sha256=hashlib.sha256(blob).hexdigest(),
                            bytes=len(blob), policy_diagnostic_present=found))
    result = dict(files=records, original_image_modified=False, code_executed=False,
                  device_identity_changed=False, root_cause_proven=False)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
