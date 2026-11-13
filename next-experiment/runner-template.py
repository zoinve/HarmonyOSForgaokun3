"""Bounded ARM/KVM full-system observation, using ARM local raw disks."""
from pathlib import Path
import json,subprocess,socket,time,hashlib
def publication_seen(text):
 import re
 return re.search(r'SAFWK: Publish SA:401 result:0(?:,|\s|$)',text) is not None
def observation_done(elapsed,bms_observed_at):
 return elapsed>=360
def validate_blocks(rows):
 expected={'d'+str(i):i!=4 for i in range(5)}
 actual={}
 for row in rows:
  name=row['device']
  if name in expected:
   assert name not in actual and 'inserted' in row,row
   assert row['inserted']['ro']==expected[name],row
   actual[name]=row
  else:
   assert 'inserted' not in row,row
 assert set(actual)==set(expected),actual
o=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/system-868')
c=json.loads((o/'config.json').read_text());report=o/'result.json';assert not report.exists()
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:name=(proc/'exe').resolve(strict=True).name
 except (FileNotFoundError,ProcessLookupError,PermissionError):continue
 assert not name.startswith('qemu-system-'),str(proc)
assert int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))>8*1024*1024
for row in c['inputs']:
 assert hashlib.sha256(Path(row['remote']).read_bytes()).hexdigest()==row['sha256']
cmd=c['command'];assert cmd[cmd.index('-m')+1]=='6144' and cmd[cmd.index('-accel')+1]=='kvm' and '-S' in cmd
def qmp(request):
 with socket.socket(socket.AF_UNIX) as s:
  s.settimeout(20);s.connect(str(o/'qmp.sock'));f=s.makefile('rwb',buffering=0)
  def receive():
   while True:
    raw=f.readline();assert raw,'QMP closed'
    msg=json.loads(raw)
    if 'return' in msg or 'error' in msg:
     assert 'error' not in msg,msg
     return msg['return']
  json.loads(f.readline());f.write(b'{"execute":"qmp_capabilities"}\n');receive()
  f.write(json.dumps(request).encode()+b'\n');return receive()
d=dict(scope='Event-aware BMS publication and normal account bootstrap observation of original HarmonyOS full system on ARM KVM with ARM local raw disks',command=cmd,memory_mb=6144,wall_limit_seconds=360,screenshots=[],desktop_verified=False,input_verified=False,policy_modified=False,identities_modified=False,guest_watchdogs_modified=False,guest_readiness_modified=False,full_disk_copies_created=1,selinux_permissive_authorized=True)
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

import shutil
protected_original=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/disks-744/userdata-analysis.img')
def original_sha():
 with protected_original.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert original_sha()=='667cbbb0658558eb2a80d13f61f5bbc6ce54e4bbd8f5c0a6817e881566ac2f56'
work=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/system-868/userdata-permissive.img');assert not work.exists()
shutil.copyfile(protected_original,work)

for row in c['disks']:
 path=Path(row['path']);assert path.is_file() and not path.is_symlink()
 assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256']
assert not any('nbd' in x for x in cmd) and '-blockdev' not in cmd
d['disk_transport']='ARM local raw files only, no NBD or cache'
d['local_before']={row['path']:row['sha256'] for row in c['disks']}
start=time.monotonic();vm=None
try:
 with (o/'serial.log').open('xb') as serial,(o/'stderr.log').open('xb') as err:
  vm=subprocess.Popen(cmd,stdout=serial,stderr=err)
  for _ in range(200):
   if (o/'qmp.sock').exists():break
   assert vm.poll() is None,'QEMU exited before QMP'
   time.sleep(.05)
  d['kvm']=qmp({'execute':'query-kvm'});assert d['kvm']['enabled']
  d['block_devices']=qmp({'execute':'query-block'});validate_blocks(d['block_devices'])
  qmp({'execute':'cont'});d['guest_started']=True
  observed=None;next_shot=60;shot=0;memory_requests=[]
  d['post_bms_publication_observation_seconds']=120
  d['memory_diagnostic_requests']=memory_requests
  d['kernel_snapshots']=[]
  while vm.poll() is None:
   elapsed=time.monotonic()-start
   text=(o/'serial.log').read_text(errors='replace')
   if observed is None and publication_seen(text):
    observed=elapsed;d['bms_publication_host_observed_seconds']=observed
   if c.get('qmp_screenshots_enabled',True) and (elapsed>=next_shot or observation_done(elapsed,observed)):
    shot+=1;target=o/f'screen-{shot}.ppm'
    try:
     qmp({'execute':'screendump','arguments':{'filename':str(target)}})
    except AssertionError as exc:
     if exc.args != ({'error':{'class':'GenericError','desc':'no surface'}},):raise
     d.setdefault('screenshot_unavailable',[]).append(dict(host_elapsed_seconds=elapsed,reason='no surface'))
    else:
     d['screenshots'].append(dict(name=target.name,host_elapsed_seconds=elapsed,bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    next_shot=180 if next_shot==60 else next_shot+120
   if observation_done(elapsed,observed):
    d['stop_reason']='bounded_360s_authorized_permissive_explicit_start'
    break
   try:vm.wait(timeout=5)
   except subprocess.TimeoutExpired:pass
  if vm.poll() is None:
   qmp({'execute':'quit'});d['host_requested_quit']=True
  vm.wait(timeout=30)
finally:
 if vm is not None and vm.poll() is None:
  vm.terminate()
  try:vm.wait(timeout=15)
  except subprocess.TimeoutExpired:vm.kill();vm.wait()
 d.update(elapsed_seconds=time.monotonic()-start,returncode=vm.returncode if vm else None,serial_sha256=hashlib.sha256((o/'serial.log').read_bytes()).hexdigest() if (o/'serial.log').exists() else None)
 d['local_after']={row['path']:sha(row['path']) for row in c['disks']}
 d['readonly_inputs_unchanged']=all(d['local_after'][row['path']]==row['sha256'] for row in c['disks'] if row['readonly'])
 d['protected_userdata_original_sha256_after']=original_sha()
 d['protected_userdata_original_unchanged']=d['protected_userdata_original_sha256_after']=='667cbbb0658558eb2a80d13f61f5bbc6ce54e4bbd8f5c0a6817e881566ac2f56'
 assert d['protected_userdata_original_unchanged']
 with report.open('x') as f:json.dump(d,f,indent=2)
print(json.dumps(d,indent=2))
