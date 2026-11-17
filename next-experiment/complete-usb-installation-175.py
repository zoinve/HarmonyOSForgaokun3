"""Finish a guarded partial installation using a hash-identical short ESP path."""
from pathlib import Path
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
REPORT = BASE.parent / 'reports/commercial61-native-175-compile-fix-1'
PAYLOAD = r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess
esp=Path('/boot/efi')
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-175')
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
original=json.loads((root/'installation-journal.json').read_text())
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)
assert 'Default Entry: '+default in status and 'Current Entry: '+default in status
assert 'OneShot Entry:' not in status
for operation,expected in [('is-enabled','enabled'),('is-active','active')]:
 assert subprocess.run(['systemctl',operation,'harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()==expected
assert subprocess.check_output(['efibootmgr','-v'],text=True)==original['firmware']
assert all(sha(esp/name)==digest for name,digest in original['efi_before'].items())
before={str(path.relative_to(esp)):sha(path) for path in esp.rglob('*') if path.is_file()}
assert set(before)-set(original['efi_before'])=={'commercial61-native-175/initrd.img'}
assert before['commercial61-native-175/initrd.img']==overlay_sha
assert sha(root/'initrd.img')==overlay_sha
for name,digest in expected_runtime.items():assert sha(root/name)==digest
assert not subprocess.run(['findmnt','-rn','-S','/dev/nvme0n1p4'],capture_output=True,text=True).stdout.strip()
alias=esp/'usb175.img'
entry=esp/'loader/entries/commercial61-native-175.conf'
assert not alias.exists() and not entry.exists()
old=(esp/'loader/entries/harmonyos-gpu-manual.conf').read_text()
options=next(line for line in old.splitlines() if line.startswith('options ')).replace('panic=0','panic=15')+' harmony.commercial=1 harmony.live_debug159=1 harmony.persistent_data166=1 harmony.usb_readonly175=1'
assert options.count('rdinit=/init ')==1
options=options.replace('rdinit=/init ','rdinit=/early-hardware093.sh ',1)
assert chain[-1]=='commercial61-native-175/initrd.img'
actual=chain[:-1]+['usb175.img']
estimated=len(options[8:])+sum(len('initrd=\\'+path.replace('/','\\'))+1 for path in actual)+1
assert estimated<1800,estimated
cluster=os.statvfs(esp).f_frsize
assert cluster>=4096 and shutil.disk_usage(esp).free>=32*1024**2+((root/'initrd.img').stat().st_size//cluster+4)*cluster
for path in actual[:-1]:assert path in original['efi_before']
text='\n'.join(['title HarmonyOS commercial ISO - protected USB storage 175 - AUTO RETURN',
 'version 6.0.0.110-original-userland','sort-key zzzz-harmony-commercial',
 'linux /native-original-graphics-045/linux',
 'devicetree /native-original-graphics-031/sc8280xp-huawei-gaokun3.dtb',
 *['initrd /'+path for path in actual],options,''])
assert len(text.encode())<cluster
(root/'installation-repair-journal.json').open('x').write(json.dumps(dict(efi_before=before,
 original_journal_sha256=sha(root/'installation-journal.json'),estimated_options_bytes=estimated,
 planned_alias=str(alias),planned_entry=str(entry)),indent=2))
with (root/'initrd.img').open('rb') as source,alias.open('xb') as target:
 shutil.copyfileobj(source,target);target.flush();os.fsync(target.fileno())
assert sha(alias)==overlay_sha
with entry.open('x') as target:target.write(text);target.flush();os.fsync(target.fileno())
os.sync()
assert all(sha(esp/name)==digest for name,digest in before.items())
after={str(path.relative_to(esp)) for path in esp.rglob('*') if path.is_file()}
assert after-set(before)=={'usb175.img','loader/entries/commercial61-native-175.conf'}
assert subprocess.check_output(['efibootmgr','-v'],text=True)==original['firmware']
assert 'Default Entry: '+default in subprocess.check_output(['bootctl','status','--no-pager'],text=True)
assert shutil.disk_usage(esp).free>=32*1024**2
result=dict(entry=str(entry),entry_text=text,initrd_sha256=overlay_sha,
 actual_initrd_chain=actual,original_admitted_chain=chain,short_alias_hash_verified=True,
 estimated_options_bytes=estimated,existing_efi_files_unchanged=len(before),
 free_bytes=shutil.disk_usage(esp).free,ubuntu_default_unchanged=True,timer_enabled=True,
 old_manual_entry_retained=True,one_shot_selected=False,reboot_requested=False,
 partial_installation_preserved=True,security_checks_changed=False,sdk_payload=False)
(root/'installation-result.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
'''


if __name__ == '__main__':
    assert not (REPORT / 'installation-result.json').exists()
    assert 'AssertionError: 1809' in (REPORT / 'installation.stderr').read_text()
    assert all(json.loads((REPORT / 'admission-test.json').read_text()).values())
    manifest = json.loads((REPORT / 'result.json').read_text())
    overlay = json.loads((REPORT / 'overlay-result.json').read_text())
    expected = {row['name']:row['sha256'] for row in manifest['artifacts']
                if row['name'] in ['init','bootstrap','bootstrap-runtime087']}
    prefix = 'chain=' + repr(overlay['chain']) + '\noverlay_sha=' + repr(overlay['sha256'])
    prefix += '\nexpected_runtime=' + repr(expected) + '\n'
    script = prefix + PAYLOAD
    compile(script, 'complete-usb-installation-175-remote', 'exec')
    (REPORT / 'installation-repair.generated.py').open('x').write(script)
    runpy.run_path(str(BASE / 'commercial-workflow-175.py'))['configure_local_transport']()
    proc = subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','HostName=192.168.10.128','-o','HostKeyAlias=192.168.10.128','matebook','sudo -n python3 -'],
        input=script,text=True,capture_output=True,timeout=180)
    (REPORT / 'installation-repair.stdout').open('x').write(proc.stdout)
    (REPORT / 'installation-repair.stderr').open('x').write(proc.stderr)
    assert proc.returncode==0,proc.stderr
    data = json.loads(proc.stdout)
    (REPORT / 'installation-result.json').open('x').write(json.dumps(data,indent=2))
    print(json.dumps(data,indent=2))
