"""Read only known adaptation-owned markers and filesystem state after Ubuntu return."""
from pathlib import Path
import json
import runpy
import subprocess
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
PAYLOAD=r'''
from pathlib import Path
import json,os,re,subprocess
device='/dev/nvme0n1p4'
target=Path('/mnt/harmony-persistent-verify-'+number)
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=120)
identity=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',device]).splitlines() if '=' in line)
assert identity['UUID']=='00029cdd-1748-4d2f-b73b-8e8164922098' and identity['TYPE']=='ext4'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
assert not target.exists()
target.mkdir(mode=0o700)
mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(target)],check=True,timeout=30)
 mounted=True
 assert target.stat().st_dev==os.stat(device).st_rdev
 data=target/'harmony-persistent-data-165/data.ext4'
 assert data.stat().st_size==8589934592 and not data.is_symlink()
 active=subprocess.run(['losetup','-j',str(data)],capture_output=True,text=True,timeout=15)
 assert active.returncode==0 and not active.stdout.strip(), 'do not inspect an active data filesystem'
 probe=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',str(data)]).splitlines() if '=' in line)
 assert probe['TYPE']=='ext4' and probe['UUID']==expected_uuid
 check=subprocess.run(['e2fsck','-f','-n',str(data)],capture_output=True,text=True,timeout=120)
 assert check.returncode==0, 'offline read-only filesystem consistency check failed'
 header=command(['dumpe2fs','-h',str(data)])
 fields=dict(line.split(':',1) for line in header.splitlines() if ':' in line)
 assert fields['Filesystem state'].strip()=='clean'
 marker=command(['debugfs','-R','cat /.harmony-persistent166/last-boot',str(data)])
 assert re.fullmatch('[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\n',marker)
 boot=marker.strip()
 assert boot==expected_boot,'disk marker must match this native runtime, not Ubuntu or a fixture'
 package_stat=command(['debugfs','-R','stat /app/el1/bundle/public/com.ohos.sceneboard',str(data)])
 scene_present='Inode:' in package_stat and 'Type: directory' in package_stat
 used=(int(fields['Block count'])-int(fields['Free blocks']))*int(fields['Block size'])
 archived={}
 if previous_boot is not None:
  assert boot!=previous_boot
  for name in ['native-perf-023.trace','native-scanout-013.ppm','native-allocator-073.trace','native-full-068','native-full-075']:
   # Existing objects are archived under the CURRENT boot identifier before services start.
   text=command(['debugfs','-R','stat /.harmony-persistent166/'+boot+'/'+name,str(data)])
   archived[name]='Inode:' in text
  assert sum(archived.values())==expected_archived,'previous boot diagnostic objects must survive instead of being overwritten'
 memory_archive=None
 if require_memory_archive:
  text=command(['debugfs','-R','stat /.harmony-persistent166/'+boot+'/commercial-memmgr108.log',str(data)])
  memory_archive='Inode:' in text and 'Type: regular' in text
  assert memory_archive
 result=dict(native_boot_id=boot,previous_native_boot_id=previous_boot,filesystem_uuid=probe['UUID'],
  data_capacity_bytes=data.stat().st_size,offline_fsck_exit=check.returncode,filesystem_clean=True,
  data_used_bytes=used,sceneboard_installed_directory_present=scene_present,
  disk_marker_matches_native_runtime=True,previous_diagnostic_objects_archived=archived,
  memory_prerequisite_log_archived=memory_archive,
  data_image_mounted=False,lab_mounted_readonly=True,original_images_modified=False)
finally:
 if mounted:subprocess.run(['umount',str(target)],check=True,timeout=60)
 target.rmdir()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''

if __name__=='__main__':
    assert sys.argv[1:] in [['166'],['167'],['168'],['169']]
    number=sys.argv[1]
    report=ROOT/('reports/commercial61-native-166-compile-fix-1' if number=='166' else 'reports/commercial61-native-'+number)
    analysis=json.loads((report/'persistent-runtime-analysis.json').read_text())
    if not analysis['native_disk_mount_and_flush_verified']:
        assert number=='167' and analysis['marker_chain_matches'] and analysis['inner_and_outer_flush_verified']
        phase=(report/'runtime-evidence/raw'/analysis['phase_file']).read_text(errors='replace')
        assert 'NATIVE_ORIGINAL001_FAIL memory prerequisite evidence 108 errno=17\n' in phase
        assert 'COMMERCIAL001_HANDOFF' not in phase
        assert analysis['backing_file_identity_and_lock_verified'] and analysis['loop_is_writable_nvme_data']
    script='number='+repr(number)+'\nexpected_uuid='+repr(analysis['filesystem_uuid'])+'\nexpected_boot='+repr(analysis['native_boot_id'])+'\nprevious_boot='+repr(analysis['previous_native_boot_id'])+'\nexpected_archived='+repr(analysis['markers'][0]['archived'])+'\nrequire_memory_archive='+repr(number in ['168','169'])+'\n'+PAYLOAD
    compile(script,'persistent-data-verification-remote','exec')
    assert not (report/'persistent-offline-verification.stdout').exists()
    runpy.run_path(str(BASE/'commercial-workflow-166.py'))['configure_local_transport']()
    proc=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','HostKeyAlias=192.168.10.128','-o','ConnectTimeout=8','zoinve@192.168.10.128',
        'sudo -n python3 -'],input=script,text=True,capture_output=True,timeout=240)
    for suffix,text in [('stdout',proc.stdout),('stderr',proc.stderr)]:
        (report/('persistent-offline-verification.'+suffix)).open('x').write(text)
    assert proc.returncode==0,proc.stderr
    result=json.loads(proc.stdout)
    result['original_init_handoff_verified']=analysis['original_init_handoff_observed']
    result['full_native_storage_acceptance']=analysis['native_disk_mount_and_flush_verified']
    (report/'persistent-offline-verification.json').open('x').write(json.dumps(result,indent=2))
    print(proc.stdout)
