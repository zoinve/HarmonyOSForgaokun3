"""Archive two unreferenced diagnostic kernels before narrowly deleting them."""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = runpy.run_path(str(ROOT / 'next-experiment/settings-workflow-254.py'))
CODE = r'''
import gzip,shutil
esp=Path('/boot/efi').resolve()
entries=esp/'loader/entries'
before={p.name:p.read_text() for p in entries.glob('*.conf')}
assert {'commercial61-native-173.conf','commercial61-native-471.conf','harmonyos-gpu-manual.conf'}<=before.keys()
refs=set()
for text in before.values():
 for line in text.splitlines():
  fields=line.split()
  if len(fields)==2 and fields[0] in ['linux','initrd','devicetree','efi']:
   refs.add(fields[1].lstrip('/'))
selected=['native-original-graphics-046/linux','native-original-graphics-047/linux']
assert not refs.intersection(selected)
for cfg in [Path('/boot/grub/grub.cfg'),*esp.rglob('*.cfg')]:
 if cfg.is_file() and cfg.stat().st_size<1024**2:
  text=cfg.read_text(errors='replace')
  assert not any(name in text for name in selected)
work=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/retired-trace-kernels-504')
assert not work.exists() and shutil.disk_usage(work.parent).free>128*1024**2
for name in selected:
 p=esp/name
 assert p.resolve().is_relative_to(esp) and stat.S_ISREG(p.lstat().st_mode)
work.mkdir(mode=0o700)
rows=[]
for name in selected:
 p=esp/name
 with p.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
 backup=work/(digest+'.gz')
 if not backup.exists():
  with p.open('rb') as source,backup.open('xb') as raw:
   with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as dest:shutil.copyfileobj(source,dest)
   raw.flush();os.fsync(raw.fileno())
  backup.chmod(0o600)
 with gzip.open(backup,'rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==digest
 rows.append(dict(path=name,bytes=p.stat().st_size,sha256=digest,archive=backup.name))
with (work/'before-removal.json').open('x') as stream:
 json.dump(dict(selected=rows,boot_references=sorted(refs)),stream,indent=2)
 stream.flush();os.fsync(stream.fileno())
assert {p.name:p.read_text() for p in entries.glob('*.conf')}==before
for row in rows:
 p=esp/row['path']
 with p.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==row['sha256']
 p.unlink()
subprocess.run(['sync','-f',str(esp)],check=True,timeout=30)
assert {p.name:p.read_text() for p in entries.glob('*.conf')}==before
print(json.dumps(dict(removed=rows,free=shutil.disk_usage(esp).free,
 all_current_menu_payloads_retained=True,ubuntu_default_preserved=True,
 original_images_modified=False,reboot_requested=False),indent=2))
'''


if __name__ == '__main__':
    report = ROOT / 'reports/unused-trace-kernels-504'
    assert not report.exists()
    report.mkdir()
    try:
        text = WORKFLOW['remote'](WORKFLOW['GUARD'] + CODE, timeout=180)
    except Exception as error:
        (report / 'failure.txt').open('x').write(str(error))
        raise
    (report / 'result.json').open('x').write(text)
    print(text)
