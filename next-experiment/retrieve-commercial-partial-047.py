"""Preserve readable evidence from a non-replayed filesystem; record every error."""
from pathlib import Path
import hashlib
import io
import json
import runpy
import subprocess
import tarfile

BASE = Path(__file__).resolve().parents[1]
DEST = BASE / 'reports/commercial61-native-047/runtime-evidence'
PAYLOAD = r'''
from pathlib import Path
import hashlib,io,json,stat,subprocess,sys,tarfile
m=Path('/mnt/commercial-return-audit-047')
assert subprocess.run(['findmnt','-rn','--source','/dev/nvme0n1p4'],capture_output=True).returncode!=0
subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec','/dev/nvme0n1p4',str(m)],check=True)
try:
 runs=list(m.glob('commercial61-native-047-*'));assert len(runs)==1
 files={};errors={};stream=io.BytesIO()
 with tarfile.open(fileobj=stream,mode='w') as archive:
  for path in sorted(runs[0].iterdir()):
   try:
    info=path.lstat();assert stat.S_ISREG(info.st_mode)
    data=path.read_bytes()
   except Exception as error:
    errors[path.name]=dict(type=type(error).__name__,errno=getattr(error,'errno',None),message=str(error));continue
   files[path.name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
   item=tarfile.TarInfo(path.name);item.size=len(data);item.mode=stat.S_IMODE(info.st_mode);item.mtime=int(info.st_mtime)
   archive.addfile(item,io.BytesIO(data))
 manifest=dict(run=runs[0].name,files=files,read_errors=errors,read_only_noload=True,partial_retrieval=True,journal_replayed=False)
 print(json.dumps(manifest),file=sys.stderr,flush=True)
 sys.stdout.buffer.write(stream.getvalue());sys.stdout.buffer.flush()
finally:subprocess.run(['umount',str(m)],check=True)
'''


def main():
    assert not DEST.exists(), 'Preserve prior retrieval'
    workflow = runpy.run_path(str(BASE / 'next-experiment/commercial-workflow-047.py'))
    workflow['configure_local_transport']()
    result = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=PAYLOAD.encode(),
                            capture_output=True, timeout=180)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    manifest = json.loads(result.stderr.decode().splitlines()[0])
    assert manifest['partial_retrieval'] and manifest['read_only_noload']
    DEST.mkdir()
    raw = DEST / 'raw'
    raw.mkdir()
    (DEST / 'original.tar').open('xb').write(result.stdout)
    with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
        for item in archive.getmembers():
            assert item.isfile() and '/' not in item.name and item.name not in ['.', '..']
            data = archive.extractfile(item).read()
            expected = manifest['files'][item.name]
            assert len(data) == expected['bytes']
            assert hashlib.sha256(data).hexdigest() == expected['sha256']
            (raw / item.name).open('xb').write(data)
    (DEST / 'retrieval-manifest.json').open('x').write(json.dumps(manifest, indent=2))
    print(json.dumps(dict(run=manifest['run'], readable_files=len(manifest['files']),
                         read_errors=manifest['read_errors'], all_readable_hashes_matched=True), indent=2))


if __name__ == '__main__':
    main()
