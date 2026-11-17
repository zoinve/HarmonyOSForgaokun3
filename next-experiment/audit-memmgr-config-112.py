"""Read supplied configuration without mounting or modifying source images."""
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
IMAGES = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092')
OUT = ROOT / 'reports/memmgr-config-audit-112'


def run(args):
    return subprocess.run(args, capture_output=True, check=True)


def inspect(image, source):
    result = run(['/usr/sbin/debugfs', '-R', 'cat ' + source, str(IMAGES / image)])
    if not result.stdout:
        assert b'File not found' in result.stderr, result.stderr
        return dict(image=image, source=source, absent=True)
    tree = ET.fromstring(result.stdout)
    name = image.split('.')[0] + '-memmgr_config.xml'
    (OUT / name).open('xb').write(result.stdout)
    leaves = []
    def walk(node, path):
        suffix = ''.join('[@' + key + '=' + value + ']' for key, value in sorted(node.attrib.items()))
        path = path + '/' + node.tag + suffix
        if len(node) == 0:
            leaves.append(dict(path=path, value=(node.text or '').strip()))
        for child in node:
            walk(child, path)
    walk(tree, '')
    return dict(image=image, source=source, bytes=len(result.stdout),
                sha256=hashlib.sha256(result.stdout).hexdigest(), leaves=leaves)


if __name__ == '__main__':
    assert not OUT.exists(), 'Evidence output already exists'
    OUT.mkdir()
    configs = [inspect('p111-system.kr990-ext4-v1.img', '/system/etc/memmgr/memmgr_config.xml'),
               inspect('p110-sys_prod.img', '/etc/memmgr/memmgr_config.xml')]
    lib = ROOT / 'reports/memmgr-initialization-audit-109/libmemmgrservice.z.so'
    assert hashlib.sha256(lib.read_bytes()).hexdigest() == '2cf2566bb7bf580513e82c6d1819775886cfe3ecd35a5e2b14a0eae60dceb012'
    for name, start, stop in [('memcg-constructor', '0x1cfaf8', '0x1cfc54'),
                              ('hyperhold-enable', '0x1db688', '0x1db7a0')]:
        result = run(['aarch64-linux-gnu-objdump', '-dC', '--start-address=' + start,
                      '--stop-address=' + stop, str(lib)])
        (OUT / (name + '.txt')).open('xb').write(result.stdout)
    result = dict(configs=configs, read_only_debugfs=True, images_mounted=False,
                  target_boot_performed=False, original_binary_modified=False,
                  desktop_verified=False)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    for config in configs:
        print(config['source'], config.get('sha256', 'absent'))
        for leaf in config.get('leaves', []):
            if any(token in leaf['path'].lower() for token in ('rootmemcg', 'sourceconfig', 'swapless', 'switch')):
                print(leaf)
