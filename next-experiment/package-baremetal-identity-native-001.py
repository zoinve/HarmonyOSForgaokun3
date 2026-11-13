"""Stage an inert base with identity-candidate modules; no device writes or boot changes."""
from pathlib import Path
import hashlib
import json
import subprocess

base=Path(__file__).resolve().parent.parent
report=base/'reports/baremetal-identity-native-package-001'
payload=r'''
from pathlib import Path
import gzip,hashlib,json,os,shutil,stat,subprocess
project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
local=project/'reports/baremetal-identity-native-package-001'
work=Path('/home/zoinve/harmony-virgl-883/baremetal-identity-native-package-001')
assert not work.exists();work.mkdir();root=work/'root';root.mkdir()
candidate=work.parent/'baremetal-identity-candidate-002';out=candidate/'out'
full=json.loads((candidate/'full-build.json').read_text());assert full['full_build_success'] and full['module_count']==391
audit=json.loads((project/'reports/baremetal-identity-candidate-002/independent-verification.json').read_text())
release='7.1.0-rc3-gaokun3-el2';prefix='lib/modules/'+release+'/'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for row in full['artifacts']:
 p=Path(row['path']);assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
parent=local/'diagnostic-base-002.cpio.gz';parent_sha='ff0a661c831f950ebad0cd69c91b21d999bffce6f2bc49601e2cb7253ab5219c'
assert sha(parent)==parent_sha
def parse(raw):
 entries={};pos=0
 while True:
  h=raw[pos:pos+110];assert len(h)==110 and h[:6]==b'070701'
  v=[int(h[6+i*8:14+i*8],16) for i in range(13)];size,ns=v[6],v[11]
  assert ns>1 and raw[pos+109+ns]==0
  name=raw[pos+110:pos+109+ns].decode();start=(pos+110+ns+3)&~3;pos=(start+size+3)&~3
  if name=='TRAILER!!!':break
  assert name not in entries and not name.startswith('/') and '..' not in Path(name).parts
  assert len(raw[start:start+size])==size
  entries[name]=(v[1],raw[start:start+size])
 return entries
old=parse(gzip.decompress(parent.read_bytes()));assert 'init' not in old and len(old)==620
preserved={n:v for n,v in old.items() if n!='lib/modules' and not n.startswith('lib/modules/')}
for name,(mode,data) in sorted(preserved.items(),key=lambda item:(len(Path(item[0]).parts),item[0])):
 p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
 if stat.S_ISDIR(mode):p.mkdir(exist_ok=True);p.chmod(stat.S_IMODE(mode))
 elif stat.S_ISREG(mode):p.write_bytes(data);p.chmod(stat.S_IMODE(mode))
 else:
  assert stat.S_ISLNK(mode);target=data.decode();assert name in ['bin/sh','sbin/modprobe'],name
  p.symlink_to(target)
modules=root/'lib/modules'/release;modules.mkdir(parents=True)
inventory=[]
for row in audit['modules']:
 p=out/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
 target=modules/'kernel'/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);target.chmod(0o644)
 assert sha(target)==row['sha256'];inventory.append(dict(path=target.relative_to(root).as_posix(),bytes=row['bytes'],sha256=row['sha256']))
assert len(inventory)==391
assert {n for n in old if n.endswith('.ko')}=={r['path'] for r in inventory}
for name in ['modules.order','modules.builtin','modules.builtin.modinfo']:
 p=out/name;assert p.is_file();shutil.copyfile(p,modules/name)
depmod=shutil.which('depmod');assert depmod,'Existing host depmod is required; do not download tools'
r=subprocess.run([depmod,'-b',str(root),'-F',str(out/'System.map'),release],capture_output=True,text=True,timeout=60)
(work/'depmod.stdout').write_text(r.stdout);(work/'depmod.stderr').write_text(r.stderr)
assert r.returncode==0 and not r.stderr.strip(),(r.returncode,r.stderr)
dep=(modules/'modules.dep').read_text();assert len(dep.splitlines())==391
for line in dep.splitlines():
 lhs,rhs=line.split(':',1)
 for rel in [lhs]+rhs.split():assert not rel.startswith('/') and '..' not in Path(rel).parts and (modules/rel).is_file(),rel
blob=bytearray();seen={}
def append(name,mode,data,ino):
 nb=name.encode()+b'\0';fields=[ino,mode,0,0,2 if stat.S_ISDIR(mode) else 1,0,len(data),0,0,0,0,len(nb),0]
 blob.extend(b'070701'+''.join(f'{v:08x}' for v in fields).encode()+nb)
 blob.extend(b'\0'*((-len(blob))%4));blob.extend(data);blob.extend(b'\0'*((-len(blob))%4))
for ino,p in enumerate(sorted(root.rglob('*')),1):
 name=p.relative_to(root).as_posix();mode=p.lstat().st_mode
 assert stat.S_ISREG(mode) or stat.S_ISDIR(mode) or stat.S_ISLNK(mode)
 data=os.readlink(p).encode() if p.is_symlink() else p.read_bytes() if p.is_file() else b''
 append(name,mode,data,ino);seen[name]=(mode,data)
append('TRAILER!!!',0,b'',len(seen)+1)
assert parse(blob)==seen and all(seen[n]==v for n,v in preserved.items())
assert not (root/'init').exists() and not any((root/'dev').iterdir())
archive=work/'diagnostic-base.cpio.gz';archive.write_bytes(gzip.compress(bytes(blob),compresslevel=6,mtime=0))
assert parse(gzip.decompress(archive.read_bytes()))==seen and sha(parent)==parent_sha
for name,source in [('linux',out/'arch/arm64/boot/Image'),('sc8280xp-huawei-gaokun3.dtb',out/'arch/arm64/boot/dts/qcom/sc8280xp-huawei-gaokun3.dtb')]:
 shutil.copyfile(source,work/name);assert sha(work/name)==sha(source)
d=dict(archive=str(archive),archive_bytes=archive.stat().st_size,archive_sha256=sha(archive),kernel_sha256=sha(work/'linux'),dtb_sha256=sha(work/'sc8280xp-huawei-gaokun3.dtb'),module_count=391,module_inventory=inventory,depmod_no_warnings=True,all_dependency_paths_present=True,nonmodule_entries_preserved=len(preserved),all_nonmodule_entries_byte_and_mode_identical=True,parent_archive_unchanged=True,archive_roundtrip_verified=True,contains_init=False,boot_entries_modified=False,native_boot_attempted=False)
(work/'result.json').write_text(json.dumps(d,indent=2)+'\n');(local/'result.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({k:v for k,v in d.items() if k!='module_inventory'},indent=2))
'''
compile(payload,'package-native-identity-001','exec')
if __name__=='__main__':
    assert not report.exists();report.mkdir()
    archive=report/'diagnostic-base-002.cpio.gz'
    subprocess.run(['scp','-o','ConnectTimeout=3','matebook:/mnt/harmony-lab/work/native-initramfs-base-002/diagnostic-base.cpio.gz',str(archive)],check=True,timeout=120)
    assert archive.stat().st_size==23909120
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='ff0a661c831f950ebad0cd69c91b21d999bffce6f2bc49601e2cb7253ab5219c'
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,capture_output=True,text=True,timeout=240)
    (report/'prepare.stdout').write_text(r.stdout);(report/'prepare.stderr').write_text(r.stderr)
    print(r.stdout);print(r.stderr);raise SystemExit(r.returncode)
