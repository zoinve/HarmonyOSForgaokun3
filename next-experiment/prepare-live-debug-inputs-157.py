"""Package the verified SSH closure on-device; never export its private key."""
from pathlib import Path
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = r'''
from pathlib import Path
import gzip,hashlib,io,json,os,tarfile
assert os.geteuid()==0
source=Path(REMOTE_ROOT)
record=json.loads((source/'preparation.json').read_text())
root=source.parent/'live-debug-inputs-157'
assert not root.exists()
root.mkdir(mode=0o700)
entries={}
for row in record['files']:
 data=(source/'root'/row['path'].lstrip('/')).read_bytes()
 assert hashlib.sha256(data).hexdigest()==row['sha256']
 entries[row['path'].lstrip('/')]=(0o755,data)
reader=(source/'root/bin/diag').read_bytes()
assert hashlib.sha256(reader).hexdigest()==record['reader_sha256']
entries['bin/diag']=(0o755,reader)
for name in ['etc/passwd','etc/group','etc/diag/authorized_keys']:
 entries[name]=(0o600,(source/'root'/name).read_bytes())
config=record['config'].replace('Port 22256','Port 22257').replace('ListenAddress 127.0.0.1','ListenAddress 192.168.10.210').replace('LogLevel VERBOSE','LogLevel ERROR')
assert 'DisableForwarding yes' in config and 'ForceCommand read-only' in config
entries['etc/ssh/sshd_config']=(0o600,config.encode())
entries['etc/diag/host_ed25519.pub']=(0o600,(record['host_public_key']+'\n').encode())
for name in ['logs/hilog','logs/native']:
 entries[name]=(0o600,b'')
directories={'etc','etc/diag','etc/ssh','root','run','run/sshd','logs','dev','bin','usr','usr/sbin','usr/lib','usr/lib/openssh','usr/lib/aarch64-linux-gnu','lib'}
for name in entries:
 directories.update(str(p) for p in Path(name).parents if str(p)!='.')
raw=io.BytesIO()
with tarfile.open(fileobj=raw,mode='w',format=tarfile.USTAR_FORMAT) as archive:
 for name in sorted(directories):
  info=tarfile.TarInfo(name);info.type=tarfile.DIRTYPE;info.mode=0o700 if name in ['root','etc/diag','logs'] else 0o755
  archive.addfile(info)
 for name,(mode,data) in sorted(entries.items()):
  info=tarfile.TarInfo(name);info.mode=mode;info.size=len(data)
  archive.addfile(info,io.BytesIO(data))
packed=gzip.compress(raw.getvalue(),compresslevel=6,mtime=0)
with tarfile.open(fileobj=io.BytesIO(packed),mode='r:gz') as archive:
 for item in archive.getmembers():
  assert not item.name.startswith('/') and '..' not in Path(item.name).parts
  assert item.isdir() or item.isfile()
  assert item.name!='etc/diag/host_ed25519'
path=root/'runtime-root.tar.gz'
path.write_bytes(packed);path.chmod(0o400)
result=dict(path=str(path),bytes=len(packed),sha256=hashlib.sha256(packed).hexdigest(),
 files=[dict(path=name,mode=oct(mode),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for name,(mode,data) in sorted(entries.items())],
 host_public_key=record['host_public_key'],reader_sha256=record['reader_sha256'],
 private_key_on_device=str(source/'root/etc/diag/host_ed25519'),private_key_in_archive=False,
 private_key_read_or_exported=False,source_images_changed=False,operational_boot_performed=False,
 listen_address='192.168.10.210',listen_port=22257)
(root/'result.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
'''


if __name__ == '__main__':
    folder = ROOT / 'reports/live-debug-inputs-157'
    assert not folder.exists()
    fixture = json.loads((ROOT / 'reports/live-debug-156/result.json').read_text())
    assert fixture['authenticated_status_verified'] and fixture['fixture_listener_stopped']
    remote = runpy.run_path(str(Path(__file__).with_name('prepare-live-debug-156.py')))['remote']
    result = remote(PAYLOAD)
    folder.mkdir()
    (folder / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps({key: result[key] for key in ['path','bytes','sha256','private_key_in_archive','private_key_read_or_exported']}, indent=2))
