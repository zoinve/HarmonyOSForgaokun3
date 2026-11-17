"""Copy ISO-verified original commercial images to NEW sparse files; no mounts."""
from pathlib import Path
import hashlib,json,subprocess,zlib
base=Path(__file__).resolve().parents[1]
source=Path('C:/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092')
manifest=json.loads((base/'reports/commercial61-iso-001/image-hashes.json').read_text())
names={'p111-system.kr990-ext4-v1.img':'system.img','p109-vendor.kr990-ext4-v1.img':'vendor.img',
 'p110-sys_prod.img':'sysprod.img','p108-chip_prod.kr990-ext4-v1.img':'chipprod.img'}
remote=r'''
from pathlib import Path
import sys,json,zlib,hashlib,os,shutil
m=json.loads(sys.argv[1]);root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-original-001')
root.mkdir(exist_ok=True)
p=root/m['dest'];partial=root/(m['dest']+'.partial')
assert not p.exists() and not partial.exists()
assert shutil.disk_usage(root).free>m['bytes']+1024**3
d=zlib.decompressobj();h=hashlib.sha256();size=0
with partial.open('xb') as out:
 while b:=sys.stdin.buffer.read(1024*1024):
  chunk=d.decompress(b);h.update(chunk);size+=len(chunk)
  for i in range(0,len(chunk),65536):
   block=chunk[i:i+65536]
   if block.count(0)==len(block):out.seek(len(block),1)
   else:out.write(block)
 tail=d.flush();assert not tail and d.eof
 assert size==m['bytes'] and h.hexdigest()==m['sha256'],(size,h.hexdigest())
 out.truncate(size);out.flush();os.fsync(out.fileno());os.fchmod(out.fileno(),0o444)
partial.rename(p)
result=dict(m,allocated_bytes=p.stat().st_blocks*512,original_images_written=False,source='ISO-verified original')
(root/(m['dest']+'.json')).open('x').write(json.dumps(result,indent=2))
print(json.dumps(result))
'''
results=[]
for m in manifest:
 p=source/m['name'];assert p.stat().st_size==m['bytes']
 meta=dict(m,dest=names[m['name']])
 args=['ssh','matebook','python3 -c '+"'"+remote.replace("'","'\"'\"'")+"' '"+json.dumps(meta)+"'"]
 proc=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 compressor=zlib.compressobj(1);h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):
   h.update(b);proc.stdin.write(compressor.compress(b))
 proc.stdin.write(compressor.flush());proc.stdin.close()
 out=proc.stdout.read();err=proc.stderr.read();assert proc.wait(timeout=120)==0,err.decode()
 assert h.hexdigest()==m['sha256']
 results.append(json.loads(out));print(out.decode(),flush=True)
(base/'reports/commercial61-native-001').mkdir(exist_ok=True)
(base/'reports/commercial61-native-001/staged-original-images.json').open('x').write(json.dumps(results,indent=2))
