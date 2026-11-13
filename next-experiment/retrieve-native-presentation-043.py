"""Read-only noload evidence capture from the unique new native043 run."""
from pathlib import Path
import hashlib
import io
import json
import re
import subprocess
import tarfile

REMOTE = r'''
from pathlib import Path
import os,subprocess,hashlib,json,sys,re
def cmd(args): return subprocess.check_output(args,text=True,timeout=30).strip()
assert os.getuid()==0 and cmd(['uname','-r'])=='7.1.0-rc3-gaokun3+'
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text()
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==expected_boot_id
device='/dev/nvme0n1p4'
assert cmd(['blkid','-s','UUID','-o','value',device])=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert cmd(['blkid','-s','PARTUUID','-o','value',device])=='24bd14b9-9d92-490a-ad15-a59c6b8e7cd9'
assert cmd(['blkid','-s','TYPE','-o','value',device])=='ext4'
assert subprocess.run(['findmnt','-rn','--source',device],capture_output=True).returncode!=0
mount=Path('/mnt/harmony-return-audit-043')
assert not mount.exists()
mount.mkdir(mode=0o700)
subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(mount)],check=True)
try:
 options=set(cmd(['findmnt','-n','-o','OPTIONS','--target',str(mount)]).split(','))
 assert {'ro','nodev','nosuid','noexec'}<=options and options.intersection({'noload','norecovery'})
 runs=list(mount.rglob('native-interactive-043-*'))
 assert len(runs)==1,[str(p) for p in runs]
 run=runs[0]
 assert run.is_dir() and not run.is_symlink()
 entries=list(run.iterdir())
 assert 0<len(entries)<=512
 files={}
 for p in entries:
  assert p.is_file() and not p.is_symlink() and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',p.name)
  assert p.stat().st_size<=64*1024*1024
  with p.open('rb') as f: h=hashlib.file_digest(f,'sha256').hexdigest()
  files[p.name]=dict(bytes=p.stat().st_size,sha256=h)
 assert sum(r['bytes'] for r in files.values())<=512*1024*1024
 print(json.dumps(dict(run=run.name,files=files,read_only_noload=True,uuid='00029cdd-1748-4d2f-b73b-8e8164922098',
  returned_boot_id=expected_boot_id,mount_options=sorted(options))),file=sys.stderr,flush=True)
 subprocess.run(['tar','-C',str(run),'-cf','-','.'],check=True)
finally:
 subprocess.run(['umount',str(mount)],check=True)
assert subprocess.run(['findmnt','-rn','--source',device],capture_output=True).returncode!=0
mount.rmdir()
'''


def validate_members(blob, manifest):
    assert len(blob) <= 514*1024*1024
    files = manifest['files']
    assert 0 < len(files) <= 512
    assert sum(r['bytes'] for r in files.values()) <= 512*1024*1024
    result = {}
    with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
        for member in archive:
            if member.isdir():
                assert member.name in ('.', './')
                continue
            name = member.name.removeprefix('./')
            assert member.isfile() and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', name)
            assert name not in result and name in files and member.size == files[name]['bytes']
            assert member.size <= 64*1024*1024
            data = archive.extractfile(member).read()
            assert len(data) == member.size and hashlib.sha256(data).hexdigest() == files[name]['sha256']
            result[name] = data
    assert set(result) == set(files)
    return result


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]/'reports/native-original-graphics-boot-043'
    dest = root/'runtime-evidence'
    assert not dest.exists()
    returned = json.loads((root/'boot-observation.json').read_text())
    assert returned['returned'] and returned['after_boot_id'] != returned['before_boot_id']
    reply = subprocess.run(['ssh','matebook','sudo -n python3 -'],
                           input=('expected_boot_id='+repr(returned['after_boot_id'])+'\n'+REMOTE).encode(),
                           capture_output=True,timeout=240)
    assert reply.returncode == 0, reply.stderr.decode(errors='replace')
    manifest = json.loads(reply.stderr.decode().splitlines()[0])
    members = validate_members(reply.stdout, manifest)
    dest.mkdir()
    (dest/'raw').mkdir()
    with (dest/'original.tar').open('xb') as f:
        f.write(reply.stdout)
    for name,data in members.items():
        with (dest/'raw'/name).open('xb') as f:
            f.write(data)
    manifest.update(all_remote_hashes_matched=True, original_partition_replayed=False,
                    unmounted_after_copy_verified=True)
    with (dest/'retrieval-manifest.json').open('x') as f:
        json.dump(manifest,f,indent=2)
    print(json.dumps(dict(run=manifest['run'],files=len(members),all_remote_hashes_matched=True,
                          original_partition_replayed=False,lab_unmounted=True)))
