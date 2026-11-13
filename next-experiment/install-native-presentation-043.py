"""Add a counted diagnostic entry and small overlay; never select or reboot it."""
from pathlib import Path
import base64
import hashlib
import json
import runpy
import subprocess


def prepare_entry(text):
    title = 'title HarmonyOS 032 - Touchpad cursor - NO AUTO REBOOT'
    assert text.count(title) == 1 and text.count('\ninitrd ') == 1
    assert text.count('options rdinit=') == 1 and text.count('panic=0') == 1
    text = text.replace(title, 'title HarmonyOS 043 - KMS completion diagnostic - AUTO RETURN')
    text = text.replace('options rdinit=', 'initrd /native-original-graphics-043/return-overlay.img\noptions rdinit=')
    return text.replace('panic=0', 'panic=15')


# Reuse only immutable read-only guard definitions, never the retired operation.
head = runpy.run_path(str(Path(__file__).with_name('archive-native-consumed-022-for-043.py')))['REMOTE']
assert head.count('\nguards()\nassert set(request') == 1
head = head.split('\nguards()\nassert set(request')[0]
REMOTE = head + r'''
import base64
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-043')
archive=root/'efi-install-043'
dest=esp/'native-original-graphics-043'
entry=esp/'loader/entries/native-original-graphics-043+1.conf'
guards()
assert rows()==request['inventory']['files'] and configs()==request['inventory']['configs']
assert root.is_dir() and not root.is_symlink() and not archive.exists()
assert not dest.exists() and not list((esp/'loader/entries').glob('native-original-graphics-043*.conf'))
assert sha(root/'result.json')==request['candidate_manifest_sha256']
for name,row in request['candidate_artifacts'].items():
 assert Path(name).name==name
 p=root/name
 assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
for name,h in {
 'native-original-graphics-032/initrd.img':'78049c130b3ab1dcd8f29d192b168bed3681d16a8aa9c298e6b548987e51f8ad',
 'native-original-graphics-031/linux':'6fa44a5f1996a82bc95e8c44b3d32a69cc14d3789e39cffa2fcafafb7c294ff5',
 'native-original-graphics-031/sc8280xp-huawei-gaokun3.dtb':'5f6b1fa73d8bffa1984710d52c0babc4df297cbb90d9f4d9a48a433a104fb016'
}.items(): assert sha(esp/name)==h
data=base64.b64decode(request['blob'],validate=True)
assert len(data)==345590 and hashlib.sha256(data).hexdigest()=='b2a0581f8869ca1d5fb6ee62bd1d0b1866c32832c73d811411f53a6f076fa3f7'
text=request['entry_text']
assert text.count('\ninitrd ')==2 and 'panic=15' in text and 'panic=0' not in text
assert shutil.disk_usage(esp).free>len(data)+len(text.encode())+64*1024*1024+65536
archive.mkdir(mode=0o700)
with (archive/'before.json').open('x') as f:
 json.dump(request['inventory'],f,indent=2);f.flush();os.fsync(f.fileno())
with (archive/'return-overlay.img').open('xb') as f:
 f.write(data);f.flush();os.fsync(f.fileno())
with (archive/'new-entry.conf').open('x') as f:
 f.write(text);f.flush();os.fsync(f.fileno())
assert sha(archive/'return-overlay.img')==hashlib.sha256(data).hexdigest()
fd=os.open(archive,os.O_RDONLY|os.O_DIRECTORY)
try: os.fsync(fd)
finally: os.close(fd)
guards()
assert rows()==request['inventory']['files'] and configs()==request['inventory']['configs']
dest.mkdir()
with (dest/'return-overlay.img').open('xb') as f:
 f.write(data);f.flush();os.fsync(f.fileno())
with entry.open('x') as f:
 f.write(text);f.flush();os.fsync(f.fileno())
os.sync()
guards()
after=rows()
old={r['path']:r for r in request['inventory']['files']}
new={r['path']:r for r in after}
assert {k:new[k] for k in old}==old
assert set(new)-set(old)=={str(entry.relative_to(esp)),str((dest/'return-overlay.img').relative_to(esp))}
assert {k:v for k,v in configs().items() if k!=str(entry.relative_to(esp))}==request['inventory']['configs']
assert sha(dest/'return-overlay.img')==hashlib.sha256(data).hexdigest() and entry.read_text()==text
free=shutil.disk_usage(esp).free
assert free>64*1024*1024
listing=json.loads(cmd(['bootctl','list','--json=short']))
counted=[r for r in listing if r.get('id','').split('+')[0].removesuffix('.conf')=='native-original-graphics-043']
assert len(counted)==1 and counted[0].get('triesLeft')==1
result=dict(boot_id=request['inventory']['boot_id'],entry=str(entry),entry_id=counted[0]['id'],
 entry_text=text,entry_sha256=sha(entry),overlay_sha256=sha(dest/'return-overlay.img'),
 old_efi_files_unchanged=len(old),efi_files_after=after,configs_after=configs(),
 firmware=request['inventory']['firmware'],free_bytes=free,minimum_free_reserve=64*1024*1024,
 ubuntu_default_unchanged=True,one_shot_selected=False,reboot_requested=False,
 target_budget_seconds=240,outer_fallback_seconds=420,hardware_watchdog=False,runtime_verified=False,
 automatic_input_injection=False,installation_journal=str(archive))
with (archive/'installation-result.json').open('x') as f:
 json.dump(result,f,indent=2);f.flush();os.fsync(f.fileno())
print(json.dumps(result))
'''

if __name__ == '__main__':
    base = Path(__file__).resolve().parents[1]
    out = base/'reports/native-presentation-043-installation.json'
    assert not out.exists()
    retired = json.loads((base/'reports/native-presentation-043-efi-archive-022.json').read_text())
    audited = json.loads((base/'reports/native-presentation-package-043-independent/result.json').read_text())
    assert audited['overlay_sha256']=='b2a0581f8869ca1d5fb6ee62bd1d0b1866c32832c73d811411f53a6f076fa3f7'
    assert audited['archive_metadata_preserved'] and audited['original_images_independent_hashes']
    assert not audited['installed'] and not audited['native_boot_attempted']
    staged = json.loads((base/'reports/native-original-graphics-boot-043/stage-result.json').read_text())
    assert staged['staged_files']==10 and not staged['runtime_launched']
    assert all(r['exit_code']==77 for r in staged['guard_checks'])
    manifest_path = base/'reports/native-original-graphics-boot-043/result.json'
    candidate = json.loads(manifest_path.read_text())
    blob = subprocess.check_output(['wsl','-d','Debian','--','cat',
        '/home/zoinve/harmony-virgl-883/native-original-graphics-boot-043/return-overlay.img'],timeout=30)
    assert len(blob)==audited['overlay_bytes'] and hashlib.sha256(blob).hexdigest()==audited['overlay_sha256']
    inventory = dict(boot_id=retired['boot_id'],files=retired['efi_files_after'],
                     configs=retired['configs_after'],firmware=retired['firmware'])
    request = dict(inventory=inventory,blob=base64.b64encode(blob).decode(),
                   entry_text=prepare_entry(inventory['configs']['loader/entries/native-original-graphics-032.conf']),
                   candidate_artifacts=candidate['artifacts'],
                   candidate_manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest())
    r = subprocess.run(['ssh','matebook','sudo -n python3 -'],input='request='+repr(request)+'\n'+REMOTE,
                       text=True,capture_output=True,timeout=180)
    if r.returncode:
        raise RuntimeError(r.stderr)
    result=json.loads(r.stdout)
    with out.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print(json.dumps({k:result[k] for k in ('entry','entry_id','old_efi_files_unchanged','free_bytes',
                                           'one_shot_selected','reboot_requested')}))
