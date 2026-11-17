"""Remove only two unreferenced ESP copies with existing verified backups."""
from pathlib import Path
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = runpy.run_path(str(ROOT / 'next-experiment/settings-workflow-254.py'))
CODE = r'''
import shutil
esp=Path('/boot/efi').resolve()
entries={p.name:p.read_text() for p in (esp/'loader/entries').glob('*.conf')}
assert {'commercial61-native-173.conf','commercial61-native-502.conf','harmonyos-gpu-manual.conf'}<=entries.keys()
refs=set()
for text in entries.values():
 for line in text.splitlines():
  fields=line.split()
  if len(fields)==2 and fields[0] in ['linux','initrd','devicetree','efi']:
   refs.add(fields[1].lstrip('/'))
selected=['set458.img','set471.img']
assert not refs.intersection(selected)
for cfg in [Path('/boot/grub/grub.cfg'),*esp.rglob('*.cfg')]:
 if cfg.is_file() and cfg.stat().st_size<1024**2:
  text=cfg.read_text(errors='replace')
  assert not any(name in text for name in selected)
rows=[]
for number in ['458','471']:
 p=esp/('set'+number+'.img')
 backup=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab')/('commercial61-native-'+number)/'initrd.img'
 assert p.resolve().is_relative_to(esp) and stat.S_ISREG(p.lstat().st_mode)
 assert backup.is_file() and p.stat().st_size==backup.stat().st_size
 for candidate in [p,backup]:
  with candidate.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==expected[number]
 rows.append(dict(path=p.name,bytes=p.stat().st_size,sha256=expected[number],existing_backup=str(backup)))
archive=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/retired-overlays-520.json')
with archive.open('x') as stream:
 json.dump(dict(selected=rows,boot_references=sorted(refs)),stream,indent=2)
 stream.flush();os.fsync(stream.fileno())
assert {p.name:p.read_text() for p in (esp/'loader/entries').glob('*.conf')}==entries
for row in rows:(esp/row['path']).unlink()
subprocess.run(['sync','-f',str(esp)],check=True,timeout=30)
print(json.dumps(dict(removed=rows,free=shutil.disk_usage(esp).free,current_payloads_retained=True,
 original_images_written=False,active_data_written=False,reboot_requested=False),indent=2))
'''

if __name__ == '__main__':
    output=ROOT/'reports/retired-overlays-520.json'
    assert not output.exists()
    expected={n:json.loads((ROOT/('reports/commercial61-native-'+n)/'overlay-result.json').read_text())['sha256']
              for n in ['458','471']}
    text=WORKFLOW['remote'](WORKFLOW['GUARD']+'\nexpected='+repr(expected)+'\n'+CODE)
    output.open('x').write(text)
    print(text)
