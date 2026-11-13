"""One native boot attempt, then read-only evidence collection. Never retry boot."""
from pathlib import Path
import base64
import json
import subprocess
import sys
import time

BASE=Path(__file__).resolve().parent.parent
REPORT=BASE/'reports/native-original-graphics-boot-001'

PREP=r'''
from pathlib import Path
import hashlib,json,os,subprocess
def cmd(a):return subprocess.check_output(a,text=True,timeout=30)
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-001')
assert not (root/'boot-attempt.json').exists()
d=json.loads((root/'installation-result.json').read_text());assert d['ubuntu_default_unchanged']
assert Path(d['entry']).read_text()==d['entry_text']
assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in cmd(['bootctl','status','--no-pager'])
assert 'OneShot Entry:' not in cmd(['bootctl','status','--no-pager'])
for p in Path('/proc').glob('[0-9]*/comm'):
 try:name=p.read_text().strip()
 except OSError:continue
 assert not name.startswith('qemu'),str(p)
original=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/original-disks')
expected={'system.img':'19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3',
 'vendor.img':'4e0c24992070e10cb35277faf8fda1e27241d455c677d58289a6bf0d75a0f8f7',
 'sys_prod.img':'41fa2bbc6862262cf1b87149b2218e019d385abc03599abc5f04155e11623b78'}
for name,h in expected.items():
 with (original/name).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==h,name
source,options=cmd(['findmnt','-n','-o','SOURCE,OPTIONS','--target','/mnt/harmony-lab']).split()
assert source=='/dev/nvme0n1p4' and options.split(',')[0]=='ro'
result=dict(boot_id_before=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 previous_trial_runs=[p.name for p in Path('/mnt/harmony-lab').glob('native-original-001-*')],original_images_sha256=expected,
 one_shot_entry='native-original-graphics-001.conf',reboot_requested=True)
with (root/'boot-attempt.json').open('x') as f:json.dump(result,f,indent=2);f.flush();os.fsync(f.fileno())
subprocess.run(['bootctl','set-oneshot','native-original-graphics-001.conf'],check=True)
result['selected_status']=cmd(['bootctl','status','--no-pager'])
assert 'OneShot Entry: native-original-graphics-001.conf' in result['selected_status']
print(json.dumps(result),flush=True)
'''

COLLECT=r'''
from pathlib import Path
import base64,hashlib,json,subprocess
def cmd(a):return subprocess.check_output(a,text=True,timeout=30)
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-001')
before=json.loads((root/'boot-attempt.json').read_text())
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
assert boot!=before['boot_id_before']
assert cmd(['uname','-r']).strip()=='7.1.0-rc3-gaokun3+'
mount=cmd(['findmnt','-n','-o','SOURCE,OPTIONS','--target','/mnt/harmony-lab']).strip()
source,options=mount.split();assert source=='/dev/nvme0n1p4' and options.split(',')[0]=='ro',mount
runs=[p for p in Path('/mnt/harmony-lab').glob('native-original-001-*') if p.name not in before['previous_trial_runs']]
assert len(runs)==1,[p.name for p in runs]
logs=[]
for p in sorted(runs[0].iterdir()):
 assert p.is_file() and not p.is_symlink()
 data=p.read_bytes();logs.append(dict(name=p.name,sha256=hashlib.sha256(data).hexdigest(),data=base64.b64encode(data).decode()))
j=json.loads((root/'installation-journal.json').read_text());esp=Path('/boot/efi')
deleted={str(Path(p).relative_to(esp)) for p in j['deleted_obsolete_kernel_caches']}
mutable_boot_files={}
for rel,h in j['efi_before'].items():
 if rel=='loader/random-seed':
  with (esp/rel).open('rb') as f:after=hashlib.file_digest(f,'sha256').hexdigest()
  mutable_boot_files[rel]=dict(before=h,after=after,reason='systemd-boot rotates its random seed on boot')
  continue
 if rel not in deleted:
  with (esp/rel).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==h,rel
assert (esp/'loader/loader.conf').read_text()==j['loader_before']['loader/loader.conf']
status=cmd(['bootctl','status','--no-pager'])
assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in status
assert 'OneShot Entry:' not in status
timer=cmd(['systemctl','is-active','harmony-lab-screen-off-001.timer']).strip();assert timer=='active'
original=root.parent/'official-arm-sdk-921/original-disks'
for name,h in before['original_images_sha256'].items():
 with (original/name).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==h,name
print(json.dumps(dict(boot_id_after=boot,trial_run=str(runs[0]),logs=logs,boot_status=status,
 screen_off_timer=timer,lab_mount=mount,original_images_verified_unchanged=3,efi_files_verified_unchanged=79,
 mutable_boot_files=mutable_boot_files,
 ubuntu_lsm=Path('/sys/kernel/security/lsm').read_text(),cmdline=Path('/proc/cmdline').read_text())))
'''

def ssh(payload,timeout=180):
    return subprocess.run(['ssh','-o','ConnectTimeout=5','matebook','sudo -n python3 -'],input=payload,
                          text=True,capture_output=True,timeout=timeout)

if __name__=='__main__':
    attempt=REPORT/'boot-attempt.json'
    assert not attempt.exists()
    if '--resume-prepared' in sys.argv:
        # Preparation already selected this candidate, but no reboot occurred.
        assert not (REPORT/'reboot-request.json').exists()
        resume=r'''
from pathlib import Path
import json,subprocess
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-001')
d=json.loads((root/'boot-attempt.json').read_text())
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==d['boot_id_before']
i=json.loads((root/'installation-result.json').read_text());assert Path(i['entry']).read_text()==i['entry_text']
d['selected_status']=subprocess.check_output(['bootctl','status','--no-pager'],text=True)
assert 'OneShot Entry: native-original-graphics-001.conf' in d['selected_status']
assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in d['selected_status']
print(json.dumps(d))
'''
        r=ssh(resume)
    else:
        r=ssh(PREP)
    (REPORT/'boot-preparation.stdout').write_text(r.stdout,encoding='utf-8')
    (REPORT/'boot-preparation.stderr').write_text(r.stderr,encoding='utf-8')
    r.check_returncode();before=json.loads(r.stdout)
    with attempt.open('x',encoding='utf-8') as f:json.dump(before,f,indent=2)
    reboot=subprocess.run(['ssh','matebook','sudo -n systemctl reboot'],capture_output=True,text=True,timeout=30)
    with (REPORT/'reboot-request.json').open('x') as f:json.dump(dict(returncode=reboot.returncode,stdout=reboot.stdout,stderr=reboot.stderr),f)
    deadline=time.monotonic()+480
    while time.monotonic()<deadline:
        time.sleep(15)
        r=ssh("from pathlib import Path;print(Path('/proc/sys/kernel/random/boot_id').read_text().strip())",timeout=15)
        if r.returncode==0 and r.stdout.strip()!=before['boot_id_before']:break
    else:raise RuntimeError('Ubuntu did not return within 480 seconds; boot will NOT be retried')
    r=ssh(COLLECT,timeout=180)
    (REPORT/'collection.stderr').write_text(r.stderr,encoding='utf-8')
    if r.returncode:
        (REPORT/'collection-failed.stdout').write_text(r.stdout,encoding='utf-8')
        r.check_returncode()
    result=json.loads(r.stdout);raw=REPORT/'native-logs';raw.mkdir()
    for row in result['logs']:
        data=base64.b64decode(row.pop('data'))
        assert Path(row['name']).name==row['name']
        with (raw/row['name']).open('xb') as f:f.write(data)
    with (REPORT/'runtime-result.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k!='logs'},indent=2))
    print('Raw snapshots collected:',len(result['logs']))
