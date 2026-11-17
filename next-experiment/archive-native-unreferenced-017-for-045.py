"""Archive one proven unreferenced EFI source copy; preserve all current menus."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess

EXPECTED = dict(path='native-original-graphics-017/initrd.img', bytes=30890833,
                sha256='7a83f050d595e41a2f70989bd35cc0f70d1cfea986648c7e86ad5a197b04f5db')


def retirement_plan(inventory):
    found = [r for r in inventory['files'] if r['path'] == EXPECTED['path']]
    assert found == [EXPECTED]
    assert not any('/native-original-graphics-017/' in text for text in inventory['configs'].values())
    return dict(EXPECTED)


policy = runpy.run_path(str(Path(__file__).with_name('native-presentation-session-045.py')))
head = runpy.run_path(str(Path(__file__).with_name('archive-native-consumed-022-for-043.py')))['REMOTE']
head = policy['timer_guard'](head.split('\nguards()\nassert set(request')[0])
REMOTE = head + r'''
guards()
assert rows()==request['inventory']['files'] and configs()==request['inventory']['configs']
source=esp/request['selected']['path']
assert source.is_file() and not source.is_symlink() and set(source.parent.iterdir())=={source}
assert not any('/native-original-graphics-017/' in text for text in configs().values())
assert source.stat().st_size==request['selected']['bytes'] and sha(source)==request['selected']['sha256']
archive=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-045/efi-archive-unreferenced-017')
assert archive.parent.is_dir() and not archive.exists()
assert shutil.disk_usage(archive.parent).free>source.stat().st_size+64*1024*1024
archive.mkdir(mode=0o700)
with (archive/'before.json').open('x') as f:
 json.dump(request,f,indent=2);f.flush();os.fsync(f.fileno())
with source.open('rb') as src, (archive/'initrd.img').open('xb') as dst:
 shutil.copyfileobj(src,dst,1024*1024);dst.flush();os.fsync(dst.fileno())
assert (archive/'initrd.img').stat().st_size==request['selected']['bytes'] and sha(archive/'initrd.img')==request['selected']['sha256']
fd=os.open(archive,os.O_RDONLY|os.O_DIRECTORY)
try: os.fsync(fd)
finally: os.close(fd)
guards()
assert rows()==request['inventory']['files'] and configs()==request['inventory']['configs']
assert not any('/native-original-graphics-017/' in text for text in configs().values())
source.unlink()
source.parent.rmdir()
os.sync()
after=rows()
assert after==[r for r in request['inventory']['files'] if r['path']!=request['selected']['path']]
assert configs()==request['inventory']['configs']
guards()
free=shutil.disk_usage(esp).free
assert free>64*1024*1024+701039+65536
result=dict(request['inventory'],files=after,efi_free=free,archive=str(archive),
 archived_file=request['selected'],all_other_efi_files_unchanged=len(after),all_current_menus_unchanged=True,
 source_copy_removed_after_verified_archive=True,screenoff_timer_inactive_disabled_preserved=True)
with (archive/'retirement-result.json').open('x') as f:
 json.dump(result,f,indent=2);f.flush();os.fsync(f.fileno())
print(json.dumps(result))
'''

if __name__ == '__main__':
    base = Path(__file__).resolve().parents[1]
    output = base/'reports/native-presentation-045-efi-archive-017.json'
    assert not output.exists()
    inventory = json.loads((base/'reports/native-presentation-045-efi-inventory-attempt-002.json').read_text())
    request = dict(inventory=inventory, selected=retirement_plan(inventory))
    result = subprocess.run(policy['SSH_BASE'] + ['matebook', 'sudo -n python3 -'],
                            input='request='+repr(request)+'\n'+REMOTE, text=True,capture_output=True,timeout=240)
    assert result.returncode == 0,result.stderr
    data = json.loads(result.stdout)
    with output.open('x') as f: json.dump(data,f,indent=2)
    print(json.dumps(dict(efi_free=data['efi_free'],unchanged=data['all_other_efi_files_unchanged'],archive=data['archive'])))
