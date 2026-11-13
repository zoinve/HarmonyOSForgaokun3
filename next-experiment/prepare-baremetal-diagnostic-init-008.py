"""Build an independent native identity/read+display diagnostic entirely in WSL."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
source=(base/'baremetal-diagnostic-init.c').read_text()
for version in ('storage-002','board-003','deadline-004','display-005','observation-006','ucsi-007','native-identity-008'):
    source=runpy.run_path(str(base/('baremetal-diagnostic-'+version+'.py')))['build_source'](source)
payload='source='+repr(source)+'\n'+r'''
from pathlib import Path
import gzip,hashlib,json,stat,subprocess
project=Path('/mnt/d/lab/HarmonyOSForMatebookego');base=project/'next-experiment';root=Path('/home/zoinve/harmony-virgl-883')
work=root/'baremetal-diagnostic-init-008';local=project/'reports/baremetal-diagnostic-init-008'
assert not work.exists() and not local.exists();work.mkdir();local.mkdir()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def parse(raw):
 entries={};pos=0
 while True:
  h=raw[pos:pos+110];assert h[:6]==b'070701' and len(h)==110
  v=[int(h[6+i*8:14+i*8],16) for i in range(13)];size,ns=v[6],v[11]
  name=raw[pos+110:pos+109+ns].decode();assert raw[pos+109+ns]==0
  start=(pos+110+ns+3)&~3;end=(start+size+3)&~3
  if name=='TRAILER!!!':return entries,pos
  assert name not in entries and len(raw[start:start+size])==size
  entries[name]=(v[1],v[2],v[3],raw[start:start+size]);pos=end
(work/'diagnostic-init.c').write_text(source)
core=[base/'baremetal-diagnostic-core.c',base/'baremetal-diagnostic-core.h']
before={p.name:sha(p) for p in core}
r=subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(core[0]),str(work/'diagnostic-init.c'),'-I',str(base),'-o',str(work/'init')],capture_output=True,text=True,timeout=90)
(local/'compile.stdout').write_text(r.stdout);(local/'compile.stderr').write_text(r.stderr);assert r.returncode==0,r.stderr
assert all(sha(p)==before[p.name] for p in core)
checked=json.loads((root/'baremetal-identity-qemu-009/result.json').read_text());assert checked['runtime_verified'] and checked['diagnostic_read_probe_verified']
helper=root/'baremetal-identity-native-read-009/sdk/native-probe'
assert (helper.parent.parent/'native-probe.c').read_bytes()==(base/'baremetal-native-identity-read-001.c').read_bytes()
meta=json.loads((root/'baremetal-identity-native-read-009/result.json').read_text());row=next(r for r in meta['ram_files'] if r['name']=='sdk/native-probe');assert sha(helper)==row['sha256'] and helper.stat().st_size==row['bytes']
package=json.loads((root/'baremetal-identity-native-package-001/result.json').read_text());parent=Path(package['archive']);assert sha(parent)==package['archive_sha256']
raw=gzip.decompress(parent.read_bytes());old,trailer=parse(raw);assert 'init' not in old and 'bin/native-identity-read-001' not in old
def member(name,mode,data,ino):
 nb=name.encode()+b'\0';v=[ino,mode,0,0,1,0,len(data),0,0,0,0,len(nb),0]
 b=b'070701'+''.join(f'{i:08x}' for i in v).encode()+nb;b+=b'\0'*((-len(b))%4);b+=data;return b+b'\0'*((-len(b))%4)
updated=raw[:trailer]+member('init',stat.S_IFREG|0o755,(work/'init').read_bytes(),0x100000)+member('bin/native-identity-read-001',stat.S_IFREG|0o755,helper.read_bytes(),0x100001)+member('TRAILER!!!',0,b'',0)
seen,_=parse(updated);assert all(seen[n]==v for n,v in old.items()) and len(seen)==len(old)+2
archive=work/'diagnostic-init.cpio.gz';archive.write_bytes(gzip.compress(updated,compresslevel=6,mtime=0));assert parse(gzip.decompress(archive.read_bytes()))[0]==seen and sha(parent)==package['archive_sha256']
d=dict(archive=str(archive),archive_bytes=archive.stat().st_size,archive_sha256=sha(archive),source_sha256=sha(work/'diagnostic-init.c'),binary_sha256=sha(work/'init'),helper_sha256=sha(helper),helper_qemu_verified=True,parent_entries_unchanged=True,archive_roundtrip_verified=True,kernel_sha256=package['kernel_sha256'],dtb_sha256=package['dtb_sha256'],modules_match_identity_candidate=True,core_source_hashes=before,native_boot_attempted=False,boot_entry_installed=False,non_pid1_refusal_verified=False)
(work/'result.json').write_text(json.dumps(d,indent=2)+'\n');(local/'result.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
'''
compile(payload,'prepare-native-diagnostic-008','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=150)
    raise SystemExit(r.returncode)
