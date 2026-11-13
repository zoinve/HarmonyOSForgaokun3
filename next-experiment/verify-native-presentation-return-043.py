"""Fresh independent evidence/Ubuntu checks; never restore entropy or set display state."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess

REMOTE = r'''
from pathlib import Path
import hashlib,json,os,runpy,subprocess,time
def cmd(args): return subprocess.check_output(args,text=True,timeout=30)
def sha(p):
 with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==expected_boot_id
assert os.uname().release=='7.1.0-rc3-gaokun3+'
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text()
assert cmd(['findmnt','-n','-o','SOURCE,FSTYPE','--target','/boot/efi']).split()==['/dev/nvme0n1p1','vfat']
assert cmd(['blkid','-s','PARTUUID','-o','value','/dev/nvme0n1p1']).strip()=='922f37b2-3474-4761-a370-5aa1dcd7c476'
status=cmd(['bootctl','status','--no-pager'])
assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in status
assert 'OneShot Entry:' not in status
assert cmd(['efibootmgr','-v'])==installation['firmware']
assert cmd(['systemctl','is-active','harmony-lab-screen-off-001.timer']).strip()=='active'
assert cmd(['systemctl','is-enabled','harmony-lab-screen-off-001.timer']).strip()=='enabled'
assert subprocess.run(['findmnt','-rn','--source','/dev/nvme0n1p4'],capture_output=True).returncode!=0
esp=Path('/boot/efi')
actual={}
for p in sorted(esp.rglob('*')):
 if p.is_file():
  assert not p.is_symlink()
  actual[str(p.relative_to(esp))]=dict(bytes=p.stat().st_size,sha256=sha(p))
before={r['path']:dict(bytes=r['bytes'],sha256=r['sha256']) for r in installation['efi_files_after']}
old='loader/entries/native-original-graphics-043+1.conf'
consumed='loader/entries/native-original-graphics-043+0-1.conf'
assert set(actual)==(set(before)-{old})|{consumed}
assert actual[consumed]==before[old]
changed=[]
for name,row in before.items():
 if name==old: continue
 if actual[name]!=row:
  assert name=='loader/random-seed',name
  changed.append(name)
assert (esp/consumed).read_text()==installation['entry_text']
assert actual['native-original-graphics-043/return-overlay.img']['sha256']==installation['overlay_sha256']
class WouldChangeDisplay(Exception): pass
def readonly_runner(args,**kwargs):
 if 'set-property' in args: raise WouldChangeDisplay('read-only verifier refuses a display setter')
 kwargs.setdefault('timeout',8)
 return subprocess.run(args,**kwargs)
screen=runpy.run_path('/usr/local/libexec/harmony-lab-screen-off-001.py')['run_once']
deadline=time.monotonic()+75
while True:
 try:
  screen_rows=screen(runner=readonly_runner)
  assert screen_rows and all(r['state']=='off' and not r['changed'] for r in screen_rows)
  break
 except WouldChangeDisplay:
  assert time.monotonic()<deadline,'Automatic screen-off not observed; no setter was invoked'
  time.sleep(1)
service=cmd(['systemctl','show','harmony-lab-screen-off-001.service','--property=Result','--property=ExecMainStatus'])
assert 'Result=success' in service and 'ExecMainStatus=0' in service
print(json.dumps(dict(boot_id=expected_boot_id,running_kernel=os.uname().release,
 ubuntu_default_preserved=True,one_shot_absent=True,original_lab_unmounted=True,
 existing_efi_hashes_unchanged=len(before)-1-len(changed),boot_managed_hash_changes=changed,
 random_seed_not_restored=True,firmware_unchanged=True,overlay_hash_matches=True,
 consumed_entry=consumed,consumed_entry_sha256=actual[consumed]['sha256'],screen_rows=screen_rows,
 screenoff_enabled_active=True,screen_state_changed_by_verifier=False,physical_screen_observed=False)))
'''


def check_file(path, row):
    assert path.is_file() and not path.is_symlink() and path.stat().st_size == row['bytes']
    with path.open('rb') as f:
        assert hashlib.file_digest(f, 'sha256').hexdigest() == row['sha256'], str(path)


if __name__ == '__main__':
    base = Path(__file__).resolve().parents[1]
    root = base/'reports/native-original-graphics-boot-043'
    output = root/'post-return-verification.json'
    assert not output.exists() and not (root/'presentation-analysis.json').exists()
    observation = json.loads((root/'boot-observation.json').read_text())
    assert observation['returned'] and observation['after_boot_id'] != observation['before_boot_id']
    installation = json.loads((base/'reports/native-presentation-043-installation.json').read_text())
    manifest = json.loads((root/'runtime-evidence/retrieval-manifest.json').read_text())
    assert manifest['read_only_noload'] and manifest['unmounted_after_copy_verified']
    assert manifest['returned_boot_id'] == observation['after_boot_id']
    assert re.fullmatch(r'native-interactive-043-[0-9a-f-]{36}', manifest['run'])
    journal = []
    modes = set()
    native_marker = False
    for name,row in manifest['files'].items():
        path = root/'runtime-evidence/raw'/name
        assert path.parent == root/'runtime-evidence/raw'
        check_file(path,row)
        raw = path.read_bytes()
        native_marker |= (b'NATIVE_DIAGNOSTIC_BEGIN release=7.1.0-rc3-gaokun3-el2' in raw
                          and b'\\native-original-graphics-043\\return-overlay.img' in raw)
        modes.update(re.findall(rb'NATIVE_GRAPHICS001_SELINUX sample=(\d+) enforce=(\d)',raw))
        journal.extend(line for line in raw.splitlines() if b'NATIVE_PRESENT043' in line)
    assert native_marker and modes and all(v == b'0' for _,v in modes)
    prior = base/'reports/native-original-graphics-boot-041/runtime-evidence'
    old = json.loads((prior/'retrieval-manifest.json').read_text())
    for name,row in old['files'].items(): check_file(prior/'raw'/name,row)
    old_trial = base/'reports/baremetal-native-trial-012-collected'
    historical = json.loads((old_trial/'collection.json').read_text())
    for row in historical['files']: check_file(old_trial/row['path'],row)
    payload = r'''
from pathlib import Path
import hashlib,json
expected={'system.img':'19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3',
'vendor.img':'4e0c24992070e10cb35277faf8fda1e27241d455c677d58289a6bf0d75a0f8f7',
'sys_prod.img':'41fa2bbc6862262cf1b87149b2218e019d385abc03599abc5f04155e11623b78'}
for name,h in expected.items():
 with (Path('/mnt/d/Download/pc_all_arm')/name).open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest()==h
print(json.dumps(dict(original_sdk_images_verified=len(expected))))
'''
    images = subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,
                            text=True,capture_output=True,timeout=180)
    assert images.returncode == 0,images.stderr
    returned = subprocess.run(['ssh','matebook','sudo -n python3 -'],
                              input='expected_boot_id='+repr(observation['after_boot_id'])+'\ninstallation='+repr(installation)+'\n'+REMOTE,
                              text=True,capture_output=True,timeout=180)
    assert returned.returncode == 0,returned.stderr
    result = json.loads(returned.stdout)
    extracted = b'\n'.join(journal)+b'\n'
    analysis = runpy.run_path(str(base/'next-experiment/analyze-native-presentation-043.py'))['analyze'](extracted)
    analysis.update(input_source='Verified raw files: only lines containing NATIVE_PRESENT043, cumulative snapshots retained',
                    input_sha256=hashlib.sha256(extracted).hexdigest())
    result.update(raw_log_sizes_and_hashes_verified=len(manifest['files']),prior041_raw_files_verified=len(old['files']),
                  older_native_raw_files_verified=len(historical['files']),original_sdk_images_verified=3,
                  native_kernel_and_overlay_markers_observed=True,selinux_evidence=sorted((int(k),int(v)) for k,v in modes),
                  completed_client=analysis['completed_client'],completed_cursor=analysis['completed_cursor'],
                  stable_120fps_verified=False,physical_screen_observed=False,hardware_watchdog=False)
    with (root/'presentation043-journal.log').open('xb') as f: f.write(extracted)
    with (root/'presentation-analysis.json').open('x') as f: json.dump(analysis,f,indent=2)
    with output.open('x') as f: json.dump(result,f,indent=2)
    print(json.dumps(dict(raw_files=result['raw_log_sizes_and_hashes_verified'],boot_id=result['boot_id'],
                          completed_client=analysis['completed_client'],completed_cursor=analysis['completed_cursor'],
                          stable_120fps_verified=False,ubuntu_default_preserved=True,lab_unmounted=True)))
