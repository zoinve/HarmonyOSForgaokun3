"""Bundle exact native helper/runtime in private storage, without host changes."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess

base = Path(__file__).resolve().parent
out = base.parent / 'reports/commercial-software-codec-bundle-072'
out.mkdir()
workflow = runpy.run_path(str(base / 'commercial-workflow-071.py'))
workflow['configure_local_transport']()
ssh = ['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
       '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
       '-o', 'ConnectTimeout=10', 'matebook']
code = r'''
from pathlib import Path
import hashlib,json,os,re,subprocess,tarfile,time
root=Path.home()/'.local/share/harmony-arm64-kvm-lab/software-codec-build-072'
result=json.loads((root/'socket-test/result.json').read_text())
assert result['all_1980_frames_match'] and result['asan_ubsan_no_report']
helper=root/'socket-test/helper'
assert hashlib.sha256(helper.read_bytes()).hexdigest()==result['helper_sha256']
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
timer=['systemctl','is-active','harmony-lab-screen-off-001.timer']
assert subprocess.check_output(timer,text=True).strip()=='active'
dest=root/'runtime';dest.mkdir(mode=0o700)
ldd=subprocess.check_output(['ldd',str(helper)],text=True)
assert 'not found' not in ldd
sources={'helper':helper}
for line in ldd.splitlines():
 match=re.fullmatch(r'\s*(\S+) => (/\S+) \(0x[0-9a-f]+\)\s*',line)
 if match:sources[match[1]]=Path(match[2]);continue
 match=re.fullmatch(r'\s*(/\S+) \(0x[0-9a-f]+\)\s*',line)
 if match:sources[Path(match[1]).name]=Path(match[1]);continue
 assert re.fullmatch(r'\s*linux-vdso.so.1 \(0x[0-9a-f]+\)\s*',line),line
assert 'ld-linux-aarch64.so.1' in sources and 'libc.so.6' in sources
rows=[]
for name,source in sorted(sources.items()):
 assert Path(name).name==name and not source.is_relative_to(dest)
 data=source.read_bytes()
 with (dest/name).open('xb') as f:f.write(data)
 (dest/name).chmod(0o555)
 rows.append(dict(name=name,source=str(source.resolve()),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
assert sum(row['bytes'] for row in rows)<512*1024*1024
listing=subprocess.run([str(dest/'ld-linux-aarch64.so.1'),'--library-path',str(dest),'--list',str(dest/'helper')],capture_output=True,text=True,timeout=30)
assert listing.returncode==0 and 'not found' not in listing.stdout,listing.stderr
for line in listing.stdout.splitlines():
 if ' => /' in line:assert str(dest)+'/' in line,line
sock=root/'runtime-probe.sock'
log=(root/'runtime-probe.stdout').open('xb');err=(root/'runtime-probe.stderr').open('xb')
proc=subprocess.Popen([str(dest/'ld-linux-aarch64.so.1'),'--library-path',str(dest),str(dest/'helper'),str(sock),'ring',str(os.getuid())],stdout=log,stderr=err)
try:
 for _ in range(100):
  assert proc.poll() is None
  if sock.exists():break
  time.sleep(.05)
 assert sock.exists()
 maps=Path('/proc/'+str(proc.pid)+'/maps').read_text()
 loaded=sorted({line.split()[-1] for line in maps.splitlines() if line.split()[-1].startswith('/')})
 assert loaded and all(path.startswith(str(dest)+'/') for path in loaded),loaded
finally:
 proc.terminate();proc.wait(timeout=10);log.close();err.close()
assert not Path(err.name).read_text()
archive=root/'software-codec-runtime-072.tar.gz'
with tarfile.open(archive,'x:gz',compresslevel=6) as tar:
 for row in rows:tar.add(dest/row['name'],arcname=row['name'],recursive=False)
data=archive.read_bytes()
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot
assert subprocess.check_output(timer,text=True).strip()=='active'
record=dict(boot_id=boot,archive=str(archive),archive_bytes=len(data),archive_sha256=hashlib.sha256(data).hexdigest(),runtime_files=rows,runtime_bytes=sum(row['bytes'] for row in rows),isolated_loader_list=listing.stdout,isolated_process_loaded_paths=loaded,isolated_startup_verified=True,isolated_decode_verified=False,system_files_modified=False,harmonyos_integrated=False,desktop_verified=False)
with (root/'runtime-bundle.json').open('x') as f:json.dump(record,f,indent=2)
print(json.dumps(record,indent=2))
'''
run = subprocess.run(ssh + ['python3 -'], input=code, text=True,
                     capture_output=True, timeout=300)
(out / 'ssh.stdout').open('x').write(run.stdout)
(out / 'ssh.stderr').open('x').write(run.stderr)
assert run.returncode == 0, run.stderr
record = json.loads(run.stdout)
(out / 'result.json').open('x').write(json.dumps(record, indent=2))
archive = out / 'software-codec-runtime-072.tar.gz'
with archive.open('xb') as target:
    transfer = subprocess.run(ssh + ['cat ' + record['archive']], stdout=target,
                              stderr=subprocess.PIPE, timeout=300)
assert transfer.returncode == 0, transfer.stderr
assert archive.stat().st_size == record['archive_bytes']
assert hashlib.sha256(archive.read_bytes()).hexdigest() == record['archive_sha256']
print(json.dumps({key: record[key] for key in ['archive_bytes', 'archive_sha256',
    'runtime_bytes', 'isolated_startup_verified', 'desktop_verified']}, indent=2))
