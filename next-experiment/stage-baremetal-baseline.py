"""Stage verified SDK originals and existing native boot baselines on new p4 only."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

assert os.geteuid() == 0
mountpoint = Path('/mnt/harmony-lab')
mount = json.loads(subprocess.check_output(
    ['findmnt', '--json', '--target', str(mountpoint)], text=True))['filesystems'][0]
assert mount['source'] == '/dev/nvme0n1p4' and mount['target'] == str(mountpoint)
uuid = subprocess.check_output(['blkid', '-s', 'UUID', '-o', 'value', mount['source']], text=True).strip()
assert uuid == '00029cdd-1748-4d2f-b73b-8e8164922098'
destination = mountpoint / 'work/baseline-001'
assert not destination.exists()
assert shutil.disk_usage(mountpoint).free > 8 * 1024 ** 3
sources = Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/original-disks')
expected = {
    'system.img': (3670016000, '19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3'),
    'vendor.img': (104857600, '4e0c24992070e10cb35277faf8fda1e27241d455c677d58289a6bf0d75a0f8f7'),
    'sys_prod.img': (1048576000, '41fa2bbc6862262cf1b87149b2218e019d385abc03599abc5f04155e11623b78'),
    'userdata.img': (104857600, '8a35c379bdb0f32e78de40881398d23733a2f384f2cdeb4a8ac431f555e81b82'),
}

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

for name, (size, digest) in expected.items():
    source = sources / name
    assert source.stat().st_size == size and sha(source) == digest, name
destination.mkdir()
sdk = destination / 'sdk-original-copies'
sdk.mkdir()
rows = []
for name, (size, digest) in expected.items():
    target = sdk / name
    shutil.copyfile(sources / name, target)
    assert target.stat().st_size == size and sha(target) == digest, name
    target.chmod(0o444)
    rows.append(dict(name=name, path=str(target), bytes=size, sha256=digest))
    print('VERIFIED_COPY', name, flush=True)
native = destination / 'native-kernel-baseline'
native.mkdir()
version = os.uname().release
for prefix in ['vmlinuz-', 'config-', 'dtb-', 'System.map-']:
    source = Path('/boot') / (prefix + version)
    assert source.is_file(), str(source)
    target = native / source.name
    before = sha(source)
    shutil.copyfile(source, target)
    assert sha(target) == before and sha(source) == before
    target.chmod(0o444)
    rows.append(dict(name=source.name, path=str(target), bytes=target.stat().st_size, sha256=before))
for name, (size, digest) in expected.items():
    assert sha(sources / name) == digest, 'Source changed: ' + name
result = dict(destination=str(destination), files=rows, sdk_originals_verified_before_after=True,
              source_boot_files_unchanged=True, boot_entries_modified=False,
              native_boot_attempted=False, kernel_release=version,
              note='Immutable baseline copies only. No HarmonyOS kernel adaptation or boot installation yet.')
(destination / 'manifest.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
