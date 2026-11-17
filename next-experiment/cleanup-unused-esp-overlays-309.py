"""Remove only retired, unreferenced standalone setNNN overlays, never shared assets."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REMOTE = r'''
from pathlib import Path
import json,os,shlex,shutil,stat,subprocess
assert os.geteuid()==0
esp=Path('/boot/efi').resolve();entries=esp/'loader/entries'
status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert 'Current Entry: '+default in status and 'Default Entry: '+default in status
assert 'OneShot Entry:' not in status
before={entry:entry.read_bytes() for entry in entries.glob('*.conf')}
assert (entries/'commercial61-native-173.conf') in before and (entries/'commercial61-native-297.conf') in before
references=set()
for data in before.values():
 for line in data.decode().splitlines():
  tokens=shlex.split(line,comments=True)
  if tokens and tokens[0] in ['linux','initrd','devicetree','efi']:
   assert len(tokens)==2 and tokens[1].startswith('/')
   references.add((esp/tokens[1].lstrip('/')).resolve())
selected=[]
for number in [197,201,206,235,253,262,266,276,285,294]:
 path=esp/('set'+str(number)+'.img')
 assert path.exists() and not path.is_symlink() and path.resolve().parent==esp
 assert path.resolve() not in references
 info=path.stat()
 assert stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_dev==esp.stat().st_dev
 selected.append((path,info.st_size,info.st_mtime_ns))
assert all(entry.read_bytes()==data for entry,data in before.items())
free_before=shutil.disk_usage(esp).free
for path,size,mtime in selected:
 assert path.stat().st_size==size and path.stat().st_mtime_ns==mtime
 path.unlink()
subprocess.run(['sync','-f',str(esp)],check=True,timeout=30)
assert all(entry.read_bytes()==data for entry,data in before.items())
assert all(path.is_file() for path in references)
print(json.dumps(dict(removed=[dict(name=p.name,bytes=n) for p,n,_ in selected],
 bytes_removed=sum(n for _,n,_ in selected),free_before=free_before,
 free_after=shutil.disk_usage(esp).free,all_active_boot_dependencies_preserved=True,
 shared_payloads_removed=False,data_images_modified=False,local_canonical_builds_removed=False,
 disk_hash_or_filesystem_suite_rerun=False),indent=2))
'''

if __name__ == '__main__':
    report=ROOT/'reports/unused-esp-overlays-cleanup-309.json'
    assert not report.exists()
    ssh=runpy.run_path(str(ROOT/'next-experiment/deploy-settings-data-198.py'))['SSH']
    result=subprocess.run(ssh+['sudo -n python3 -'],input=REMOTE,text=True,capture_output=True,timeout=50)
    assert result.returncode==0,result.stderr
    json.loads(result.stdout)
    report.open('x').write(result.stdout)
    print(result.stdout)
