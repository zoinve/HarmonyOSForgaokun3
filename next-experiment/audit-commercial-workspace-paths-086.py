"""Audit external workspace candidates without modifying original images."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMAGES = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092')
FILES = {
    '/system': 'p111-system.kr990-ext4-v1.img',
    '/sys_prod': 'p110-sys_prod.img',
    '/chip_prod': 'p108-chip_prod.kr990-ext4-v1.img',
    '/chipset': 'p109-vendor.kr990-ext4-v1.img',
}
PATHS = ('etc/hw_launcher_default_workspace.json',
         'etc/hw_launcher_2in1_pc_workspace.json')


def main():
    folder = ROOT / 'reports/commercial-workspace-paths-audit-086'
    folder.mkdir(exist_ok=False)
    results = []
    for root, image in FILES.items():
        for relative in PATHS:
            internal = ('/system/' if root == '/system' else '/') + relative
            result = subprocess.run(
                ['debugfs', '-R', 'cat ' + internal, str(IMAGES / image)],
                capture_output=True, check=True)
            diagnostic = result.stderr.decode('utf-8', errors='replace')
            missing = 'File not found by ext2_lookup' in diagnostic
            entry = dict(policy_root=root, image=image, internal_path=internal,
                         stderr=diagnostic, missing=missing, bytes=len(result.stdout))
            if not missing:
                entry['json'] = json.loads(result.stdout)
                entry['sha256'] = hashlib.sha256(result.stdout).hexdigest()
            else:
                assert not result.stdout
            results.append(entry)
    output = dict(read_only=True, operational_boot_performed=False,
                  note='Policy roots follow existing platform defaults; runtime custom roots are not established.',
                  candidates=results)
    with (folder / 'result.json').open('x') as stream:
        json.dump(output, stream, indent=2)
    print(json.dumps(dict(candidates=len(results), missing=sum(r['missing'] for r in results))))


if __name__ == '__main__':
    main()
