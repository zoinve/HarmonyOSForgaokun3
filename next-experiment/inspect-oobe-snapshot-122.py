"""Inspect real SettingsData schema on a target-private clone, never export DBs."""
from pathlib import Path
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

REMOTE = r'''
from pathlib import Path
import hashlib,json,os,sqlite3,stat,subprocess

root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/oobe-snapshot-inspection-122')
assert os.geteuid()==0 and not root.exists() and not root.is_symlink()
assert not subprocess.run(['findmnt','-rn','--source','/dev/nvme0n1p4'],capture_output=True).stdout.strip()
assert subprocess.check_output(['blkid','-s','UUID','-o','value','/dev/nvme0n1p4'],text=True).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert subprocess.run(['systemctl','is-active','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='active'
root.mkdir(mode=0o700)
lab=root/'lab-ro';lab.mkdir(mode=0o700)
data=root/'data-clone-mount';data.mkdir(mode=0o700)
clone=root/'data-working.ext4'
def digest(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec','/dev/nvme0n1p4',str(lab)],check=True)
try:
 source=lab/'private-oobe121/data.ext4'
 assert source.is_file() and not source.is_symlink() and source.stat().st_size==8589934592
 assert stat.S_IMODE(source.stat().st_mode)==0o600 and source.stat().st_uid==0
 before=digest(source)
 assert not clone.exists()
 subprocess.run(['cp','--sparse=always','--reflink=auto','--no-clobber',str(source),str(clone)],check=True)
 assert digest(clone)==before and digest(source)==before
finally:subprocess.run(['umount',str(lab)],check=True)
assert clone.resolve().parent==root.resolve() and clone.is_file() and not clone.is_symlink()
assert clone.stat().st_size==8589934592
check=subprocess.run(['e2fsck','-fy',str(clone)],capture_output=True)
(root/'clone-e2fsck.stdout').open('xb').write(check.stdout)
(root/'clone-e2fsck.stderr').open('xb').write(check.stderr)
assert check.returncode in (0,1),check.returncode
result=dict(source_snapshot_sha256=before,source_snapshot_unchanged=True,
 raw_data_exported=False,clone_e2fsck_status=check.returncode,settings_modified=False,databases=[])
subprocess.run(['mount','-t','ext4','-o','loop,nodev,nosuid,noexec',str(clone),str(data)],check=True)
try:
 directory=data/'app/el1/0/database/com.ohos.settingsdata/entry/rdb'
 assert directory.is_dir() and not directory.is_symlink()
 result['rdb_directory']=str(directory.relative_to(data))
 result['directory_files']=sorted(p.name for p in directory.iterdir())
 for name in ('settingsdata.db','settingsdata_slave.db'):
  path=directory/name
  assert path.is_file() and not path.is_symlink()
  st=path.stat()
  entry=dict(name=name,bytes=st.st_size,uid=st.st_uid,gid=st.st_gid,mode=oct(stat.S_IMODE(st.st_mode)),
   xattr_names=os.listxattr(path),tables=[],settings={})
  if 'security.selinux' in entry['xattr_names']:
   entry['selinux_label']=os.getxattr(path,'security.selinux').rstrip(b'\0').decode('ascii')
  connection=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
  try:
   connection.execute('PRAGMA query_only=ON')
   integrity=connection.execute('PRAGMA integrity_check').fetchall()
   assert integrity==[('ok',)], 'clone database integrity check failed'
   entry['integrity_check']='ok'
   for table,sql in connection.execute("SELECT name,sql FROM sqlite_master WHERE type='table' ORDER BY name"):
    quoted='"'+table.replace('"','""')+'"'
    columns=connection.execute('PRAGMA table_info('+quoted+')').fetchall()
    entry['tables'].append(dict(name=table,sql=sql,columns=[dict(name=r[1],type=r[2],pk=r[5]) for r in columns]))
   for table,key in [('SETTINGSDATA','device_provisioned'),('USER_SETTINGSDATA_SECURE_100','user_setup_complete')]:
    assert any(t['name']==table for t in entry['tables']), 'required original table absent'
    rows=connection.execute('SELECT VALUE FROM "'+table+'" WHERE KEYWORD=?',(key,)).fetchall()
    assert len(rows)<=1
    value=rows[0][0] if rows else None
    assert value in (None,'0','1',0,1), 'unexpected non-boolean setup value; refusing export'
    entry['settings'][key]=value
  finally:connection.close()
  entry['sidecars']={suffix:dict(bytes=Path(str(path)+suffix).stat().st_size) for suffix in ('-wal','-shm','-journal','-dwr') if Path(str(path)+suffix).exists()}
  result['databases'].append(entry)
finally:subprocess.run(['umount',str(data)],check=True)
assert not subprocess.run(['findmnt','-rn','--source','/dev/nvme0n1p4'],capture_output=True).stdout.strip()
(root/'inspection-result.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
'''


if __name__ == '__main__':
    report = ROOT / 'reports/oobe-snapshot-inspection-122'
    assert not report.exists()
    prior = ROOT / 'reports/commercial61-native-121'
    assert json.loads((prior / 'boot-observation.json').read_text())['returned']
    preservation = json.loads((prior / 'post-return-verification.json').read_text())
    assert preservation['lab_partition_unmounted'] and preservation['ubuntu_current_and_default']
    manifest = json.loads((prior / 'runtime-evidence/retrieval-manifest.json').read_text())
    found = False
    for name in manifest['files']:
        if not name.startswith('phase-'):
            continue
        raw = (prior / 'runtime-evidence/raw' / name).read_bytes()
        import hashlib
        assert hashlib.sha256(raw).hexdigest() == manifest['files'][name]['sha256']
        if b'OOBE121_CAPTURE_RESULT status=0 thaw=0' in raw:
            found = True
    assert found, 'No verified completed and thawed snapshot; do not use partial data'
    report.mkdir()
    (report / 'remote.py').open('x').write(REMOTE)
    runpy.run_path(str(BASE / 'commercial-workflow-121.py'))['configure_local_transport']()
    result = subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','HostName=192.168.10.128','-o','HostKeyAlias=192.168.10.128','matebook','sudo -n python3 -'],
        input=REMOTE,text=True,capture_output=True,timeout=300)
    (report / 'stdout').open('x').write(result.stdout)
    (report / 'stderr').open('x').write(result.stderr)
    assert result.returncode == 0, result.stderr
    parsed = json.loads(result.stdout)
    assert parsed['raw_data_exported'] is False and parsed['settings_modified'] is False
    (report / 'result.json').open('x').write(json.dumps(parsed,indent=2))
    print(result.stdout)
