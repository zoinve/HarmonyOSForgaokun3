"""Read-only post-cleanup baseline for minimally archiving obsolete candidate005 assets."""
from pathlib import Path
import json
import subprocess

out=Path(__file__).resolve().parent.parent/'reports/baremetal-efi-space-audit-002.json'
payload=r'''
from pathlib import Path
import hashlib,json,shutil,subprocess
esp=Path('/boot/efi');lab=Path('/mnt/harmony-lab')
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text().split()
assert not list((esp/'loader/entries').glob('harmony-native-diag-*'))
assert not (esp/'harmony-native-diag-014').exists()
assets={}
for directory in sorted(esp.glob('harmony-native-diag-*')):
 assert directory.is_dir() and not directory.is_symlink()
 rows=[]
 for p in sorted(directory.iterdir()):
  assert p.is_file() and not p.is_symlink()
  with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
  rows.append(dict(name=p.name,bytes=p.stat().st_size,sha256=digest))
 assets[directory.name]=rows
print(json.dumps(dict(free=shutil.disk_usage(esp).free,lab_free=shutil.disk_usage(lab).free,
 assets=assets,boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 configs={str(p):p.read_text() for p in (esp/'loader').rglob('*.conf')},
 efi=subprocess.check_output(['efibootmgr','-v'],text=True,timeout=15))))
'''
if __name__=='__main__':
    assert not out.exists()
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],input=payload,text=True,capture_output=True,timeout=60)
    assert r.returncode==0,r.stderr
    result=json.loads(r.stdout);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(free=result['free'],oldest_assets=next(iter(result['assets'])),boot_id=result['boot_id'])))
