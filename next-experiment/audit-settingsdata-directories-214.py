"""Compare public SettingsData directory metadata only; never copy app/account data."""
from pathlib import Path, PurePosixPath
import ctypes
import json
import os
import runpy
import subprocess
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
BUILD=Path('/home/zoinve/harmony-virgl-883')
REPORT=ROOT/'reports/settingsdata-directories-214'
BUNDLE='com.ohos.settingsdata'
FIXED={'app','app/el1','app/el1/0'}
for category in ['base','database','log','aot_compiler']:
    FIXED.add('app/el1/0/'+category)
    FIXED.add('app/el1/0/'+category+'/'+BUNDLE)


def selected(name):
    prefix='./.hmos-data/'
    if not name.startswith(prefix):return None
    relative=name[len(prefix):].rstrip('/')
    path=PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or str(path)!=relative:return None
    if relative in FIXED:return relative
    if any(relative.startswith('app/el1/0/'+category+'/'+BUNDLE+'/')
           for category in ['base','database','log','aot_compiler']):return relative
    return None


def source():
    reader=runpy.run_path(str(BASE/'audit-settings-seed-183.py'))
    rows=[]
    def consume(name,size,kind,lib,archive,entry):
        relative=selected(name)
        if relative is None or kind!=0o40000:return
        for function,result in [('archive_entry_uid',ctypes.c_longlong),
                                ('archive_entry_gid',ctypes.c_longlong),('archive_entry_perm',ctypes.c_uint)]:
            method=getattr(lib,function);method.argtypes=[ctypes.c_void_p];method.restype=result
        rows.append(dict(path=relative,uid=lib.archive_entry_uid(entry),gid=lib.archive_entry_gid(entry),
                         mode=lib.archive_entry_perm(entry)))
    scan=reader['scan_archive'](select=lambda name:False,consume=consume)
    assert len({row['path'] for row in rows})==len(rows)
    return dict(source_entries_inspected=scan['entries_inspected'],directory_metadata=rows,
        app_file_contents_read=False,files_extracted=False,target_modified=False,
        account_activation_identity_state_read=False)


REMOTE=r'''
from pathlib import Path
import hashlib,json,os,subprocess
def digest(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
device='/dev/nvme0n1p4';mount=Path('/mnt/settingsdata214')
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
 assert digest(image)==expected_sha
 rows=[]
 for relative in paths:
  assert relative.startswith('app/') or relative=='app'
  outputs={}
  for operation in ['stat','ea_list']:
   proc=subprocess.run(['debugfs','-R',operation+' /'+relative,str(image)],capture_output=True,text=True,timeout=30)
   assert proc.returncode==0
   outputs[operation]=proc.stdout
  rows.append(dict(path=relative,present='Inode:' in outputs['stat'],metadata=outputs))
 assert digest(image)==expected_sha
 result=dict(candidate_sha256=expected_sha,directories=rows,bytes_unchanged=True,
  read_only_noload=True,app_file_contents_read=False,repair_requested=False)
finally:
 if mounted:subprocess.run(['umount',str(mount)],check=True)
 mount.rmdir()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''


if __name__=='__main__':
    assert sys.argv[1:] in [['source'],['target']]
    REPORT.mkdir(exist_ok=True);mode=sys.argv[1]
    output=REPORT/(mode+'.json');assert not output.exists()
    if mode=='source':result=source()
    else:
        prior=json.loads((REPORT/'source.json').read_text())
        paths=sorted(FIXED|{row['path'] for row in prior['directory_metadata']})
        offline=json.loads((ROOT/'reports/commercial61-native-206/settings-data-offline-212.json').read_text())
        assert offline['filesystem_clean']
        code='paths='+repr(paths)+'\nexpected_sha='+repr(offline['candidate_sha256_after_boot'])+'\n'+REMOTE
        compile(code,'settingsdata214-remote','exec')
        runpy.run_path(str(BASE/'commercial-workflow-206.py'))['configure_local_transport']()
        ssh=runpy.run_path(str(BASE/'deploy-settings-data-198.py'))['SSH']
        proc=subprocess.run(ssh+['sudo -n python3 -'],input=code,text=True,capture_output=True,timeout=300)
        for suffix,data in [('stdout',proc.stdout),('stderr',proc.stderr)]:
            (REPORT/(mode+'.'+suffix)).open('x').write(data)
        assert proc.returncode==0,proc.stderr
        result=json.loads(proc.stdout)
    output.open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
