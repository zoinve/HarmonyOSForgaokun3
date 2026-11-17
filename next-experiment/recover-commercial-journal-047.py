"""Replay journal only in an independent metadata image; read original data RO."""
from pathlib import Path
import hashlib
import io
import json
import runpy
import subprocess
import tarfile

BASE = Path(__file__).resolve().parents[1]
DEST = BASE / 'reports/commercial61-native-047/recovered-evidence'
PAYLOAD = r'''
from pathlib import Path
import hashlib,io,json,math,os,re,shutil,stat,subprocess,sys,tarfile
device='/dev/nvme0n1p4'
work=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial-recovery-047')
assert not work.exists()
assert shutil.disk_usage(work.parent).free>4*1024**3
assert subprocess.run(['findmnt','-rn','--source',device],capture_output=True).returncode!=0
fd=os.open(device,os.O_RDONLY|os.O_CLOEXEC)
before=os.pread(fd,4096,1024)
assert before[56:58]==b'\x53\xef'
work.mkdir(mode=0o700)
image=work/'metadata.img'
def command(args,name,timeout=300):
 r=subprocess.run(args,capture_output=True,timeout=timeout)
 (work/(name+'.stdout')).open('xb').write(r.stdout)
 (work/(name+'.stderr')).open('xb').write(r.stderr)
 return r
r=command(['e2image','-r',device,str(image)],'e2image')
assert r.returncode==0,r.stderr.decode(errors='replace')
assert image.is_file() and not image.is_symlink()
def sparse_hash(path):
 result=[]
 with path.open('rb') as f:
  pos=0
  while pos<path.stat().st_size:
   try:start=os.lseek(f.fileno(),pos,os.SEEK_DATA)
   except OSError as error:
    if error.errno==6:break
    raise
   end=os.lseek(f.fileno(),start,os.SEEK_HOLE)
   f.seek(start);h=hashlib.sha256();left=end-start
   while left:
    block=f.read(min(left,1024**2));assert block;h.update(block);left-=len(block)
   result.append(dict(start=start,end=end,sha256=h.hexdigest()));pos=end
 return result
baseline=dict(bytes=image.stat().st_size,allocated=image.stat().st_blocks*512,extents=sparse_hash(image))
(work/'metadata-before.json').open('x').write(json.dumps(baseline,indent=2))
# This argument is a newly created regular file, never the original block device.
assert image.resolve().parent==work.resolve() and stat.S_ISREG(image.stat().st_mode)
r=command(['e2fsck','-y','-E','journal_only',str(image)],'journal-replay')
assert r.returncode in [0,1],r.stdout.decode(errors='replace')+r.stderr.decode(errors='replace')
assert os.pread(fd,4096,1024)==before
run='commercial61-native-047-52a7e50d-5fa5-482f-a771-df64fc0b4aa8'
names=['phase-%03d.log'%i for i in range(1,41)]+['interactive-hilog030.log','interactive-faults030.log']
files={};errors={};mapping={};output=work/'recovered';output.mkdir()
for name in names:
 path='/'+run+'/'+name
 r=subprocess.run(['debugfs','-R','stat '+path,str(image)],capture_output=True,text=True,timeout=30)
 (work/(name+'.stat')).open('x').write(r.stdout+r.stderr)
 size=re.search(r'\bSize:\s*(\d+)',r.stdout)
 if r.returncode or not size or 'Type: regular' not in r.stdout:
  errors[name]=dict(stage='replayed_inode',output=r.stdout+r.stderr);continue
 size=int(size[1]);assert 0<=size<=16*1024**2
 data=bytearray();blocks=[]
 for logical in range(math.ceil(size/4096)):
  r=subprocess.run(['debugfs','-R','bmap '+path+' '+str(logical),str(image)],capture_output=True,text=True,timeout=30)
  value=r.stdout.strip()
  assert r.returncode==0 and re.fullmatch(r'\d+',value),(name,logical,r.stdout,r.stderr)
  physical=int(value)
  assert 0<physical<16777216,(name,logical,physical)
  block=os.pread(fd,4096,physical*4096);assert len(block)==4096
  blocks.append(dict(logical=logical,physical=physical,sha256=hashlib.sha256(block).hexdigest()))
  data.extend(block)
 data=bytes(data[:size]);(output/name).open('xb').write(data)
 files[name]=dict(bytes=size,sha256=hashlib.sha256(data).hexdigest())
 mapping[name]=blocks
assert os.pread(fd,4096,1024)==before
os.close(fd)
assert subprocess.run(['findmnt','-rn','--source',device],capture_output=True).returncode!=0
manifest=dict(run=run,files=files,errors=errors,journal_replayed_on_copy_only=True,
 original_opened_read_only=True,original_superblock_unchanged=True,original_unmounted=True,
 metadata_copy=str(image),metadata_before=baseline,source_blocks=mapping,
 content_from_original_data_blocks=True,recovered_not_original_retrieval=True)
(work/'recovery-manifest.json').open('x').write(json.dumps(manifest,indent=2))
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as archive:
 for path in sorted(output.iterdir()):archive.add(path,arcname='raw/'+path.name,recursive=False)
 for name in ['recovery-manifest.json','metadata-before.json','e2image.stdout','e2image.stderr','journal-replay.stdout','journal-replay.stderr']:
  archive.add(work/name,arcname=name,recursive=False)
'''


def main():
    assert not DEST.exists(), 'Preserve recovery evidence'
    workflow = runpy.run_path(str(BASE / 'next-experiment/commercial-workflow-047.py'))
    workflow['configure_local_transport']()
    result = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=PAYLOAD.encode(),
                            capture_output=True, timeout=1200)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    DEST.mkdir()
    (DEST / 'original.tar').open('xb').write(result.stdout)
    with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
        for item in archive.getmembers():
            path = Path(item.name)
            assert item.isfile() and not path.is_absolute() and '..' not in path.parts
            assert len(path.parts) == 1 or path.parts[0] == 'raw' and len(path.parts) == 2
            target = DEST / path
            target.parent.mkdir(exist_ok=True)
            target.open('xb').write(archive.extractfile(item).read())
    manifest = json.loads((DEST / 'recovery-manifest.json').read_text())
    previous = json.loads((DEST.parent / 'runtime-evidence/retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        data = (DEST / 'raw' / name).read_bytes()
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
    comparisons = {name: item == manifest['files'].get(name) for name, item in previous['files'].items()}
    (DEST / 'comparison.json').open('x').write(json.dumps(comparisons, indent=2))
    assert all(comparisons.values()), comparisons
    print(json.dumps(dict(recovered_files=len(manifest['files']),errors=manifest['errors'],
                         previous_readable_files_identical=len(comparisons),
                         original_unmounted=manifest['original_unmounted'],
                         original_superblock_unchanged=manifest['original_superblock_unchanged']),indent=2))


if __name__ == '__main__':
    main()
