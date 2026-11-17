"""Read-only LAB capacity and top-level image allocation audit."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REMOTE = r'''
from pathlib import Path
import json,os,shutil,subprocess
device='/dev/nvme0n1p4';mount=Path('/mnt/lab-space-219')
assert not mount.exists()
assert subprocess.check_output(['blkid','-p','-s','UUID','-o','value',device],text=True).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
mount.mkdir(mode=0o700);mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(mount)],check=True);mounted=True
 assert mount.stat().st_dev==os.stat(device).st_rdev
 rows=[]
 for directory in sorted(mount.iterdir()):
  if directory.is_symlink() or not directory.is_dir():continue
  for path in sorted(directory.iterdir()):
   if not path.is_symlink() and path.is_file():
    info=path.stat()
    if info.st_size>=64*1024**2:
     rows.append(dict(path=str(path.relative_to(mount)),bytes=info.st_size,allocated_bytes=info.st_blocks*512))
 usage=shutil.disk_usage(mount)
 result=dict(total_bytes=usage.total,free_bytes=usage.free,large_files=rows,
  new216_candidate_exists=(mount/'harmony-settings-data-216').exists(),
  read_only_noload=True,file_contents_read=False,target_files_changed=False)
finally:
 if mounted:subprocess.run(['umount',str(mount)],check=True)
 mount.rmdir()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    report = ROOT / 'reports/lab-space-219'
    assert not report.exists()
    report.mkdir()
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    result = subprocess.run(ssh + ['sudo -n python3 -'], input=REMOTE,
        capture_output=True, text=True, timeout=90)
    for suffix, data in [('stdout', result.stdout), ('stderr', result.stderr)]:
        (report / suffix).open('x').write(data)
    assert result.returncode == 0, result.stderr
    record = json.loads(result.stdout)
    (report / 'result.json').open('x').write(json.dumps(record, indent=2))
    print(result.stdout)
