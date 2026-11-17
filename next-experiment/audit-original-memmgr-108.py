"""Read the supplied memory-service launch chain without changing any image."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMAGE = '/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img'
OUT = ROOT / 'reports/original-memmgr-audit-108'
PATHS = [
    '/system/etc/init/memmgrservice.cfg', '/system/profile/memmgrservice.json',
    '/system/bin/l410_memmgr_nohyperhold_ns_exec_v1',
    '/system/bin/l410_tokenized_service_launcher_memmgr_v1',
    '/system/lib64/libmemmgrclient.z.so',
]


if __name__ == '__main__':
    assert not OUT.exists()
    content = {}
    for path in PATHS:
        result = subprocess.run(['/usr/sbin/debugfs', '-R', 'cat ' + path, IMAGE], capture_output=True, check=True)
        assert result.stdout and b'File not found' not in result.stderr, path
        content[path] = result.stdout
    config = json.loads(content[PATHS[0]])
    profile = json.loads(content[PATHS[1]])
    assert len(config['services']) == 1 and config['services'][0]['name'] == 'memmgrservice'
    assert profile['systemability'][0]['name'] == 1909
    assert 'start memmgrservice' in config['jobs'][0]['cmds']
    OUT.mkdir()
    files = []
    for path, data in content.items():
        name = Path(path).name
        (OUT / name).open('xb').write(data)
        item = dict(source=path, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), elf=data.startswith(b'\x7fELF'))
        if item['elf']:
            for suffix, command in [('strings', ['strings', '-a']), ('symbols', ['aarch64-linux-gnu-readelf', '-Ws'])]:
                output = subprocess.check_output(command + [str(OUT / name)])
                (OUT / (name + '.' + suffix + '.txt')).open('xb').write(output)
        files.append(item)
    disassembly = subprocess.check_output(['aarch64-linux-gnu-objdump', '-d', '-C',
        '--start-address=0x1222c', '--stop-address=0x12500', str(OUT / 'libmemmgrclient.z.so')])
    (OUT / 'memmgr-client-get-service.disassembly.txt').open('xb').write(disassembly)
    result = dict(files=files, service=config['services'][0], jobs=config['jobs'], profile=profile,
        read_only_debugfs=True, original_image_mounted=False, original_binary_modified=False,
        launch_failure_cause_not_yet_proven=True, target_boot_performed=False, desktop_verified=False)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(files=files, launch_chain=config['services'][0]['path'], target_boot_performed=False), indent=2))
