"""Second initramfs replaces only /init; retain the complete original 032 archive."""
import subprocess
payload=r'''
from pathlib import Path
import gzip,hashlib,json,stat,io
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'native-original-graphics-boot-033'
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/native-original-graphics-boot-033')
def parse(p):
 b=gzip.decompress(p.read_bytes());out={};pos=0
 while pos<len(b):
  assert b[pos:pos+6]==b'070701'
  v=[int(b[pos+6+i*8:pos+14+i*8],16) for i in range(13)]
  size=v[6];n=v[11];name=b[pos+110:pos+110+n-1].decode();pos=(pos+110+n+3)&~3
  data=b[pos:pos+size];pos=(pos+size+3)&~3
  if name=='TRAILER!!!':break
  out[name]=(v[1],data)
 return out
old=parse(root/'native-original-graphics-boot-032/initrd.img');new=parse(work/'initrd.img')
assert old.keys()==new.keys()
changed=[n for n in old if old[n]!=new[n]]
assert set(changed)=={'init','native-target/scratch-data.ext4'},changed
# The builder creates a fresh empty volatile filesystem with a new UUID.
# Reuse the byte-identical 032 scratch image; no target data is persisted in it.
new['native-target/scratch-data.ext4']=old['native-target/scratch-data.ext4']
assert new['init'][1]==(work/'init').read_bytes()
def member(name,mode,data,ino):
 name=name.encode()+b'\0'
 fields=[ino,mode,0,0,1,0,len(data),0,0,0,0,len(name),0]
 out=b'070701'+b''.join(f'{v:08x}'.encode() for v in fields)+name
 out+=b'\0'*((-len(out))%4);out+=data;out+=b'\0'*((-len(data))%4)
 return out
raw=member('init',new['init'][0],new['init'][1],1)+member('TRAILER!!!',0,b'',2)
dest=work/'return-overlay.img'
with dest.open('xb') as f:f.write(gzip.compress(raw,mtime=0))
assert parse(dest)=={'init':new['init']}
# Kernel concatenated initramfs semantics: the last archive replaces /init.
assert parse(root/'native-original-graphics-boot-032/initrd.img')|parse(dest)==new
r=dict(overlay_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,
 only_changed_member=['init'],fresh_unused_033_scratch_not_installed=True,base_candidate=32,outer_deadline_seconds=420,target_budget_seconds=240,
 interactive_manual_exit=False,automatic_input_injection=False,runtime_verified=False,
 parent_result_metadata_superseded=['outer_deadline_seconds','original_service_observation_seconds','interactive_manual_exit'])
for p in [work/'return-overlay-result.json',local/'return-overlay-result.json']:
 with p.open('x') as f:json.dump(r,f,indent=2)
print(json.dumps(r))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
