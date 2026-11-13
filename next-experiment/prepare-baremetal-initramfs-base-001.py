"""Package an inert diagnostic base, with offline ARM64 userspace checks only."""
from pathlib import Path
import json
import subprocess

report = Path(__file__).resolve().parent.parent / 'reports/baremetal-initramfs-base-001.json'
assert not report.exists()
payload = r'''
from pathlib import Path
import gzip,hashlib,json,os,re,shutil,stat,subprocess
work=Path('/mnt/harmony-lab/work')
assert subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(work)],text=True).strip()=='/dev/nvme0n1p4'
assert subprocess.check_output(['findmnt','-n','-o','UUID','--target',str(work)],text=True).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
dest=work/'native-initramfs-base-001';assert not dest.exists()
modules=work/'native-module-root-001'
module_report=json.loads((modules/'preparation-result.json').read_text())
assert module_report['depmod_no_warnings'] and module_report['module_count']==391
release=module_report['kernel_release'];assert release=='7.1.0-rc3-gaokun3-el2'
firmware=work/'firmware-baseline-001'
firmware_report=json.loads((firmware/'manifest.json').read_text())
assert firmware_report['files_verified']==12
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
# Inventory sources before creating any output, including generated module indexes.
sources={}
for p in (modules/'lib/modules'/release).rglob('*'):
 if p.is_file():sources['lib/modules/'+release+'/'+p.relative_to(modules/'lib/modules'/release).as_posix()]=p
assert sum(name.endswith('.ko') for name in sources)==391
for row in firmware_report['files']:
 p=firmware/'lib/firmware'/row['name'];assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
 sources['lib/firmware/'+row['name']]=p
busybox=Path('/usr/bin/busybox');assert busybox.is_file()
elf=busybox.read_bytes();assert elf[:4]==b'\x7fELF' and int.from_bytes(elf[18:20],'little')==183
# Static BusyBox has no PT_INTERP, independently checked rather than trusting ldd's exit status.
phoff=int.from_bytes(elf[32:40],'little');phsize=int.from_bytes(elf[54:56],'little');phnum=int.from_bytes(elf[56:58],'little')
assert all(int.from_bytes(elf[phoff+i*phsize:phoff+i*phsize+4],'little')!=3 for i in range(phnum))
sources['bin/busybox']=busybox
for name,target in [('kmod','bin/kmod'),('blkid','sbin/blkid')]:
 p=Path(shutil.which(name) or '/usr/sbin/'+name).resolve(strict=True);sources[target]=p
 r=subprocess.run(['ldd',str(p)],capture_output=True,text=True,check=True)
 assert 'not found' not in r.stdout,r.stdout
 libs=re.findall(r'(?:=>\s+|^\s*)(/[^\s]+)',r.stdout,re.M)
 assert any('ld-linux-aarch64' in lib for lib in libs),r.stdout
 for lib in libs:
  source=Path(lib);assert source.is_file();sources[lib.lstrip('/')]=source
before={name:dict(bytes=p.stat().st_size,sha256=sha(p)) for name,p in sources.items()}
dest.mkdir();root=dest/'root';root.mkdir()
for directory in ['bin','sbin','etc/modprobe.d','proc','sys','dev','run','tmp','mnt/lab']:(root/directory).mkdir(parents=True,exist_ok=True)
for name,p in sources.items():
 target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
 target.chmod(0o755 if p.stat().st_mode & 0o111 else 0o644)
 assert sha(target)==before[name]['sha256']
for target,link in [('busybox','bin/sh'),('../bin/kmod','sbin/modprobe')]:os.symlink(target,root/link)
assert not (root/'init').exists() and not any((root/'dev').iterdir())
env=dict(os.environ);env.pop('MODPROBE_OPTIONS',None)
checks=[]
commands=[['/bin/busybox','sh','-c','printf OFFLINE_ARM64_SHELL_OK'],['/bin/kmod','--version'],['/sbin/blkid','--version']]
commands += [['/sbin/modprobe','--config','/etc/modprobe.d','--set-version',release,'--show-depends',n] for n in ['nvme','msm','panel_himax_hx83121a','i2c_hid_of','huawei_gaokun_ec','qcom_wdt']]
for command in commands:
 r=subprocess.run(['/usr/sbin/chroot',str(root)]+command,capture_output=True,text=True,env=env,timeout=30)
 checks.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 assert r.returncode==0 and not r.stderr.strip(),checks[-1]
assert checks[0]['stdout']=='OFFLINE_ARM64_SHELL_OK'
assert not any((root/'dev').iterdir())
assert all(sha(p)==before[name]['sha256'] for name,p in sources.items())
# Root-owned reproducible newc; no device nodes, host /init, credentials, or boot entries.
blob=bytearray();inventory={}
def append(name,mode,data,ino):
 nb=name.encode()+b'\0';fields=[ino,mode,0,0,2 if stat.S_ISDIR(mode) else 1,0,len(data),0,0,0,0,len(nb),0]
 blob.extend(b'070701'+''.join(f'{v:08x}' for v in fields).encode()+nb)
 blob.extend(b'\0'*((-len(blob))%4));blob.extend(data);blob.extend(b'\0'*((-len(blob))%4))
for ino,p in enumerate(sorted(root.rglob('*')),1):
 name=p.relative_to(root).as_posix();st=p.lstat()
 assert stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode) or stat.S_ISLNK(st.st_mode)
 data=os.readlink(p).encode() if p.is_symlink() else p.read_bytes() if p.is_file() else b''
 append(name,st.st_mode,data,ino);inventory[name]=(st.st_mode,data)
append('TRAILER!!!',0,b'',len(inventory)+1)
# Independent parse-back verifies mode, content, names, padding, and every entry.
pos=0;seen={}
while True:
 h=blob[pos:pos+110];assert h[:6]==b'070701'
 mode=int(h[14:22],16);size=int(h[54:62],16);ns=int(h[94:102],16)
 name=bytes(blob[pos+110:pos+109+ns]).decode();start=(pos+110+ns+3)&~3;pos=(start+size+3)&~3
 if name=='TRAILER!!!':break
 assert name not in seen and not Path(name).is_absolute() and '..' not in Path(name).parts
 seen[name]=(mode,bytes(blob[start:start+size]))
assert seen==inventory and 'init' not in seen
archive=dest/'diagnostic-base.cpio.gz';archive.write_bytes(gzip.compress(bytes(blob),compresslevel=6,mtime=0))
result=dict(destination=str(dest),archive=str(archive),archive_bytes=archive.stat().st_size,archive_sha256=sha(archive),
 kernel_release=release,module_count=391,firmware_files=12,archive_entries=len(inventory),archive_roundtrip_verified=True,
 offline_checks=checks,source_files_unchanged=True,contains_init=False,bootable_diagnostic_ready=False,
 firmware_scope='board/Adreno subset only; not complete Wi-Fi closure',installed_to_host=False,
 modules_loaded=False,boot_entries_modified=False,native_boot_attempted=False)
(dest/'manifest.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
'''
compile(payload, 'prepare-inert-diagnostic-base', 'exec')
r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=payload,
                   text=True, capture_output=True, timeout=600)
if r.returncode:
    print(r.stdout)
    print(r.stderr)
    r.check_returncode()
result = json.loads(r.stdout)
assert result['archive_roundtrip_verified'] and not result['contains_init']
report.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({k: result[k] for k in ['destination', 'archive_bytes', 'archive_sha256',
                                      'module_count', 'firmware_files', 'contains_init', 'native_boot_attempted']}, indent=2))
