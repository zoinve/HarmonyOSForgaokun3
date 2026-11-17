"""Diagnose both ext4 layers read-only; export compact structural error counts."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/settings-storage-inspection-242.json'
REMOTE = r'''
from pathlib import Path
import hashlib,json,os,re,subprocess
device='/dev/nvme0n1p4'
mount=Path('/mnt/settings-inspection-242')
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=300)
def digest(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def inspect(path):
 result=subprocess.run(['e2fsck','-f','-n',str(path)],capture_output=True,text=True,timeout=300)
 text=result.stdout+'\n'+result.stderr
 patterns={'journal_recovery_skipped':r'skipping journal recovery',
 'orphan_linked_list':r'orphan.*(?:linked list|inode)',
 'bitmap_difference':r'(?:Block|Inode) bitmap differences',
 'free_count_wrong':r'Free (?:blocks|inodes) count wrong',
 'directory_corruption':r'directory corrupted|directory.*corrupt|invalid.*directory|directory.*invalid',
 'inode_checksum':r'inode.*checksum|checksum.*inode',
 'multiply_claimed':r'multiply.claimed',
 'unconnected_inode':r'Unattached inode|unconnected inode',
 'filesystem_errors_remain':r'FILESYSTEM STILL HAS ERRORS'}
 header=command(['dumpe2fs','-h',str(path)])
 fields=dict(line.split(':',1) for line in header.splitlines() if ':' in line)
 return dict(exit_status=result.returncode,diagnostic_bytes=len(text.encode()),
  diagnostic_sha256=hashlib.sha256(text.encode()).hexdigest(),
  diagnostic_counts={name:len(re.findall(pattern,text,re.I)) for name,pattern in patterns.items()},
  filesystem_state=fields.get('Filesystem state','').strip(),
  filesystem_features=fields.get('Filesystem features','').strip(),
  repair_requested=False)
assert command(['blkid','-p','-s','UUID','-o','value',device]).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
outer=inspect(device)
assert not mount.exists()
mount.mkdir(mode=0o700);mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(mount)],check=True);mounted=True
 assert mount.stat().st_dev==os.stat(device).st_rdev
 candidate=mount/'harmony-settings-data-197/data.ext4'
 assert not candidate.is_symlink() and not command(['losetup','-j',str(candidate)]).strip()
 before=digest(candidate)
 inner=inspect(candidate)
 assert digest(candidate)==before
 active=digest(mount/'harmony-persistent-data-165/data.ext4')
 assert active=='36246b8dc557f2385a8491e3e6d32aaddccad2974f0603f127c335f2b38a9dce'
 result=dict(outer_lab=outer,inner_candidate=inner,candidate_sha256=before,
  active165_sha256=active,active165_unchanged=True,candidate_unchanged_by_inspection=True,
  outer_mounted_readonly_noload=True,boot_requested=False,repair_requested=False)
finally:
 if mounted:subprocess.run(['umount',str(mount)],check=True,timeout=60)
 mount.rmdir()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    assert not REPORT.exists()
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    proc = subprocess.run(ssh + ['sudo -n python3 -'], input=REMOTE, text=True,
                          capture_output=True, timeout=900)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    REPORT.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
