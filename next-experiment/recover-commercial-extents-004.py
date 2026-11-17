"""Use clone-recovered leaf extents to read unchanged original data blocks read-only."""
from pathlib import Path
import subprocess,json,tarfile,io,hashlib
root=Path(__file__).resolve().parents[1]/'reports/commercial61-native-004/runtime-evidence'
assert not root.exists()
code=r'''
from pathlib import Path
import os,re,subprocess,hashlib,json,tarfile,io,sys
work=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-evidence-recovery-004');clone=work/'metadata-clone.img'
run='commercial61-native-004-b97a1618-df38-4db9-9c12-90a2367fc47b'
assert subprocess.run(['findmnt','-rn','-S','/dev/nvme0n1p4'],capture_output=True).returncode!=0
def debug(cmd):
 r=subprocess.run(['debugfs','-R',cmd,str(clone)],capture_output=True,text=True,check=True)
 assert not any(x in r.stderr for x in ['not found','Filesystem not open','checksum']),r.stderr
 return r.stdout
header=subprocess.check_output(['dumpe2fs','-h',str(clone)],stderr=subprocess.DEVNULL,text=True)
block=int(re.search(r'Block size:\s*(\d+)',header)[1]);assert block==4096
entries=debug('ls -p /'+run);fd=os.open('/dev/nvme0n1p4',os.O_RDONLY|os.O_CLOEXEC)
pattern=re.compile(r'^\s*\d+\s*/\s*\d+\s+\d+\s*/\s*\d+\s+(\d+)\s*-\s*(\d+)\s+(\d+)\s*-\s*(\d+)\s+(\d+)\s*(.*)$')
files={}
try:
 with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as tf:
  for line in entries.splitlines():
   fields=line.split('/')
   if len(fields)<8 or not fields[2].startswith('100'):continue
   inode,name,size=int(fields[1]),fields[5],int(fields[6]);assert '/' not in name and name not in ['.','..']
   detail=debug('dump_extents -l <'+str(inode)+'>');data=bytearray(size);extents=[];nextblock=0
   for text in detail.splitlines():
    m=pattern.match(text)
    if not m:continue
    first,last,physical,physical_last,count=map(int,m.groups()[:5]);flags=m[6].strip()
    assert not flags and first==nextblock and last-first+1==count and physical_last-physical+1==count,(name,text)
    length=min(count*block,size-first*block);assert length>0
    chunk=os.pread(fd,length,physical*block);assert len(chunk)==length
    data[first*block:first*block+length]=chunk;nextblock=last+1
    extents.append(dict(logical_block=first,physical_block=physical,blocks=count,bytes=length,sha256=hashlib.sha256(chunk).hexdigest()))
   assert nextblock==(size+block-1)//block,(name,size,detail)
   files[name]=dict(bytes=size,sha256=hashlib.sha256(data).hexdigest(),zero_bytes=data.count(0),inode=inode,extents=extents)
   member=tarfile.TarInfo(name);member.size=size;tf.addfile(member,io.BytesIO(data))
finally:os.close(fd)
manifest=dict(run=run,files=files,method='journal replay on new metadata clone; original data extents read via O_RDONLY',original_partition_replayed=False,clone_file_data_used=False,block_size=block)
(work/'extent-recovery-manifest.json').open('x').write(json.dumps(manifest,indent=2))
print(json.dumps(manifest),file=sys.stderr)
'''
r=subprocess.run(['ssh','matebook','sudo -n python3 -'],input=code.encode(),capture_output=True,timeout=240)
assert r.returncode==0,r.stderr.decode(errors='replace')
m=json.loads(r.stderr);root.mkdir();raw=root/'raw';raw.mkdir();(root/'original.tar').open('xb').write(r.stdout)
with tarfile.open(fileobj=io.BytesIO(r.stdout)) as tf:
 for t in tf:
  assert t.isfile() and '/' not in t.name and t.name not in ['.','..']
  data=tf.extractfile(t).read();assert hashlib.sha256(data).hexdigest()==m['files'][t.name]['sha256']
  (raw/t.name).open('xb').write(data)
(root/'retrieval-manifest.json').open('x').write(json.dumps(m,indent=2))
print(json.dumps(dict(run=m['run'],files=len(m['files']),hashes_matched=True,streams={n:m['files'][n] for n in ['interactive-hilog030.log','interactive-faults030.log']}),indent=2))
