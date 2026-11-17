"""Preserve bounded disassembly of the supplied SDK's initialization lock."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT / 'reports/commercial61-native-105/devicemanager-static/libdevicemanagersdk.z.so'
OUT = ROOT / 'reports/commercial61-native-107/sdk-lock-audit'


if __name__ == '__main__':
    assert not OUT.exists()
    data = SDK.read_bytes()
    assert len(data) == 687304
    image = '/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img'
    original = subprocess.run(['/usr/sbin/debugfs', '-R', 'cat /system/lib64/platformsdk/libdevicemanagersdk.z.so', image], capture_output=True, check=True)
    assert original.stdout == data, 'SDK differs from supplied image'
    ranges = {'proxy': (0x764dc, 0x766dc), 'init': (0x78014, 0x7861c), 'request': (0x78ec8, 0x79158)}
    artifacts = {}
    outputs = {}
    for name, (start, end) in ranges.items():
        disassembly = subprocess.check_output(['aarch64-linux-gnu-objdump', '-d', '-C',
            f'--start-address={start:#x}', f'--stop-address={end:#x}', str(SDK)])
        outputs[name] = disassembly
        artifacts[name] = dict(start=start, end=end, sha256=hashlib.sha256(disassembly).hexdigest())
    init = outputs['init'].decode()
    request = outputs['request'].decode()
    assert re.search(r'780c8:.*add\s+x19, x0, #0x8', init)
    assert re.search(r'780d8:.*mutex::lock', init)
    assert re.search(r'782e0:.*blr\s+x8', init)
    assert re.search(r'784a0:.*mutex::unlock', init)
    assert init.count('mutex::lock') == init.count('mutex::unlock') == 1
    assert re.search(r'78f18:.*add\s+x19, x0, #0x8', request)
    assert re.search(r'78f30:.*mutex::lock', request)
    result = dict(sdk_sha256=hashlib.sha256(data).hexdigest(), sdk_bytes=len(data),
        input_matches_read_only_source_image=True, disassembly=artifacts,
        init_lock_address=0x780d8, init_ipc_call_address=0x782e0, init_unlock_address=0x784a0,
        send_request_lock_address=0x78f30, manager_mutex_field_offset=8,
        static_init_lock_spans_ipc_call=True, same_runtime_manager_instance_proven=False,
        original_binary_modified=False, original_image_mounted=False, desktop_verified=False)
    OUT.mkdir()
    for name, body in outputs.items():
        (OUT / (name + '.disassembly.txt')).open('xb').write(body)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
