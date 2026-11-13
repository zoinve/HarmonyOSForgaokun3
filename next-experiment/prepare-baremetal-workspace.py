"""Create only the explicitly authorized 64 GiB partition in verified free space.

Run as root on MateBook. Never rerun after a partially completed operation.
No existing filesystem, EFI contents or boot entries are changed.
"""
from pathlib import Path
import hashlib
import json
import os
import pwd
import subprocess

assert os.geteuid() == 0
disk = '/dev/nvme0n1'
device = '/dev/nvme0n1p4'
backup = Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/baremetal-partition-backup-20261111')
report = backup / 'workspace-created.json'
assert not report.exists() and not Path(device).exists()
env = dict(os.environ, LC_ALL='C')

def run(args):
    result = subprocess.run(args, capture_output=True, text=True, env=env, check=True)
    return result.stdout

def table():
    return json.loads(run(['sfdisk', '--json', disk]))['partitiontable']

manifest = json.loads((backup / 'manifest.json').read_text())
for name, row in manifest.items():
    body = (backup / name).read_bytes()
    assert len(body) == row['bytes'] and hashlib.sha256(body).hexdigest() == row['sha256']
before = json.loads((backup / 'partitiontable.json').read_text())['partitiontable']
assert table() == before
assert len(before['partitions']) == 3
start, sectors = 211814400, 134217728
end = start + sectors - 1
assert start % 2048 == 0 and sectors * 512 == 64 * 1024 ** 3
for row in before['partitions']:
    assert end < row['start'] or start >= row['start'] + row['size']
mountpoint = Path('/mnt/harmony-lab')
assert not mountpoint.exists(), 'Do not overwrite an existing mount directory'
boot_before = run(['efibootmgr', '-v'])
assert boot_before == (backup / 'efi-boot.txt').read_text()

creation = run(['sgdisk', f'--new=4:{start}:{end}', '--typecode=4:8300',
                '--change-name=4:HarmonyOS-lab', disk])
(backup / 'partition-create.log').write_text(creation)
after = table()
assert after['id'] == before['id'] and len(after['partitions']) == 4
for old in before['partitions']:
    assert next(row for row in after['partitions'] if row['node'] == old['node']) == old
new = next(row for row in after['partitions'] if row['node'] == device)
assert new['start'] == start and new['size'] == sectors and new['name'] == 'HarmonyOS-lab'
if not Path(device).exists():
    run(['partx', '--add', '--nr', '4', disk])
run(['udevadm', 'settle', '--timeout=20'])
assert Path(device).is_block_device()
assert int(run(['blockdev', '--getsize64', device])) == 64 * 1024 ** 3
assert not any(device in line for line in Path('/proc/mounts').read_text().splitlines())
format_log = run(['mkfs.ext4', '-L', 'harmony-lab', '-m', '0',
                  '-E', 'nodiscard,lazy_itable_init=0,lazy_journal_init=0', device])
(backup / 'format-new-partition.log').write_text(format_log)
mountpoint.mkdir()
run(['mount', '-o', 'nodev,nosuid', device, str(mountpoint)])
mount = json.loads(run(['findmnt', '--json', '--target', str(mountpoint)]))['filesystems'][0]
assert mount['source'] == device and mount['target'] == str(mountpoint) and mount['fstype'] == 'ext4'
owner = pwd.getpwnam('zoinve')
work = mountpoint / 'work'
work.mkdir()
os.chown(work, owner.pw_uid, owner.pw_gid)
note = mountpoint / 'README.txt'
note.write_text('Independent 64 GiB HarmonyOS bare-metal development workspace.\n'
                'Existing Ubuntu/EFI/swap partitions preserved. No native boot image installed yet.\n'
                'Mounted manually; no fstab or default boot change was made.\n')
probe = work / '.write-verification'
payload = b'HarmonyOS isolated workspace write verification\n'
probe.write_bytes(payload)
with probe.open('rb') as stream:
    os.fsync(stream.fileno())
assert probe.read_bytes() == payload
probe.unlink()
verification = run(['sgdisk', '--verify', disk])
assert 'No problems found' in verification, verification
assert run(['efibootmgr', '-v']) == boot_before
final = table()
for old in before['partitions']:
    assert next(row for row in final['partitions'] if row['node'] == old['node']) == old
result = dict(device=device, bytes=sectors * 512, first_sector=start, last_sector=end,
              mountpoint=str(mountpoint), workspace=str(work),
              filesystem_uuid=run(['blkid', '-s', 'UUID', '-o', 'value', device]).strip(),
              original_partition_records_unchanged=True, boot_entries_unchanged=True,
              workspace_write_read_verified=True, fstab_modified=False,
              baremetal_boot_installed=False, gpt_verification=verification,
              space=run(['df', '-B1', str(mountpoint)]))
report.write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
