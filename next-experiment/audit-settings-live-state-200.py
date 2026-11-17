'''Read only persisted BMS/token state; export selected metadata, never token values.'''
from pathlib import Path
import json
import runpy
import subprocess
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REPORT=ROOT/'reports/settings-live-state-200'
QUERY=r'''
from pathlib import Path
import hashlib,json,os,re,sqlite3,subprocess,tempfile
BUNDLE='com.huawei.hmos.settings'
def digest(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dicts(value):
 if isinstance(value,dict):
  yield value
  for child in value.values():yield from dicts(child)
 elif isinstance(value,list):
  for child in value:yield from dicts(child)
def inspect_data(image):
 os.umask(0o077)
 databases={}
 with tempfile.TemporaryDirectory(prefix='settings-state200-') as directory:
  for kind,relative in [('main','bms/bundle_manager_service/bmsdb.db'),
                        ('slave','bms/bundle_manager_service/bmsdb_slave.db'),
                        ('token_main','access_token/access_token.db'),
                        ('token_slave','access_token/access_token_slave.db')]:
   target=Path(directory)/kind;target.mkdir(mode=0o700)
   for suffix in ['', '-wal', '-shm']:
    result=subprocess.run(['debugfs','-R','cat /service/el1/public/'+relative+suffix,str(image)],capture_output=True,timeout=60)
    assert result.returncode==0
    if not result.stdout:
     assert suffix, 'required source database missing'
     continue
    if not suffix:assert result.stdout.startswith(b'SQLite format 3\0')
    (target/('state.db'+suffix)).open('xb').write(result.stdout)
   connection=sqlite3.connect((target/'state.db').as_uri()+'?mode=ro',uri=True)
   try:
    connection.execute('PRAGMA query_only=ON')
    assert connection.execute('PRAGMA integrity_check').fetchall()==[('ok',)]
    summary=dict(sqlite_integrity_ok=True,main_file_sha256=digest(target/'state.db'),
     wal_bytes=(target/'state.db-wal').stat().st_size if (target/'state.db-wal').exists() else 0,
     raw_values_exported=False)
    tokens=set()
    if not kind.startswith('token_'):
     rows=[]
     for key,value in connection.execute('SELECT KEY, VALUE FROM installed_bundle'):
      if not isinstance(key,str) or not re.fullmatch(re.escape(BUNDLE)+r'(?:_\d+)?',key):continue
      users=[];abilities=[]
      for node in dicts(json.loads(value)):
       user=node.get('bundleUserInfo')
       if isinstance(user,dict):
        users.append(dict(user_id=user.get('userId'),uid=node.get('uid'),enabled=user.get('enabled')))
        token=node.get('accessTokenId')
        if user.get('userId')==100 and isinstance(token,int) and token>0:tokens.add(token)
       if node.get('bundleName')==BUNDLE and node.get('name')=='com.huawei.hmos.settings.MainAbility':
        abilities.append(dict(name=node['name'],enabled=node.get('enabled'),module_name=node.get('moduleName')))
      rows.append(dict(bundle_key=key,users=users,main_abilities=abilities))
     summary['settings_bundle_rows']=rows
    else:
     matches=0
     for (table,) in connection.execute('SELECT name FROM sqlite_master WHERE type=?',('table',)):
      assert re.fullmatch(r'[A-Za-z0-9_]+',table)
      columns=[row[1] for row in connection.execute('PRAGMA table_info('+table+')')]
      keys=[name.replace('_','').lower() for name in columns]
      if not all(name in keys for name in ['bundlename','userid','tokenid']):continue
      for row in connection.execute('SELECT * FROM '+table):
       if row[keys.index('bundlename')]!=BUNDLE or row[keys.index('userid')]!=100:continue
       matches+=1;token=row[keys.index('tokenid')]
       if isinstance(token,int) and token>0:tokens.add(token)
     summary['settings_user100_token_records']=matches
    databases[kind]=(summary,tokens)
   finally:connection.close()
  pairs={kind:len(databases[kind][1])==1 and databases[kind][1]==databases['token_'+kind][1]
         for kind in ['main','slave']}
  return dict(databases={kind:row[0] for kind,row in databases.items()},unique_settings_user100_token_match=pairs,
   original_signature_checks_changed=False,raw_token_values_exported=False,private_copies_removed_on_exit=True,
   database_records_not_modified=True,live_ability_launch_verified=False)
'''
TARGET=r'''
device='/dev/nvme0n1p4';mount=Path('/mnt/settings-state200')
assert not mount.exists()
assert subprocess.check_output(['blkid','-p','-o','value','-s','UUID',device],text=True).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
mount.mkdir(mode=0o700);mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(mount)],check=True);mounted=True
 assert mount.stat().st_dev==os.stat(device).st_rdev
 image=mount/'harmony-settings-data-197/data.ext4'
 assert not image.is_symlink() and image.stat().st_size==8589934592
 assert not subprocess.check_output(['losetup','-j',str(image)],text=True).strip()
 assert digest(image)=='41fae8e1ceacedd356da6e6d712aa8a995179c042221657f4d8e2deace9938c6'
 result=inspect_data(image)
 assert digest(image)=='41fae8e1ceacedd356da6e6d712aa8a995179c042221657f4d8e2deace9938c6'
 result.update(native_run='commercial61-native-087-76d33584-471a-4e78-bab5-e417a6d5c30b',
  candidate_bytes_unchanged_by_query=True,lab_mounted_readonly_noload=True)
finally:
 if mounted:subprocess.run(['umount',str(mount)],check=True)
 mount.rmdir()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''


if __name__=='__main__':
    assert sys.argv[1:] in [['local-source'],['target']]
    mode=sys.argv[1];REPORT.mkdir(exist_ok=True)
    output=REPORT/(mode+'.json');assert not output.exists()
    if mode=='local-source':
        code=QUERY+"\nprint(json.dumps(inspect_data(Path('/home/zoinve/harmony-virgl-883/settings-data-candidate-191-r2/data.ext4')),indent=2))\n"
        compile(code,'settings-source200','exec')
        result=subprocess.run(['python3','-c',code],capture_output=True,text=True,timeout=300)
    else:
        code=QUERY+TARGET;compile(code,'settings-target200','exec')
        ssh=runpy.run_path(str(BASE/'deploy-settings-data-198.py'))['SSH']
        result=subprocess.run(ssh+['sudo -n python3 -'],input=code,text=True,capture_output=True,timeout=300)
    for suffix,data in [('stdout',result.stdout),('stderr',result.stderr)]:
        (REPORT/(mode+'.'+suffix)).open('x').write(data)
    assert result.returncode==0,result.stderr
    output.open('x').write(json.dumps(json.loads(result.stdout),indent=2))
    print(result.stdout)
