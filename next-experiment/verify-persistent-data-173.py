"""Require a clean inactive filesystem and preserved per-boot diagnostic history."""
from pathlib import Path
import json
import re
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-173'

if __name__ == '__main__':
    assert not (REPORT / 'persistent-offline-verification.stdout').exists()
    analysis = json.loads((REPORT / 'persistent-runtime-analysis.json').read_text())
    assert analysis['native_disk_mount_and_flush_verified']
    assert json.loads((REPORT / 'post-return-verification.json').read_text())['lab_partition_unmounted']
    names = re.findall(r'"([A-Za-z0-9_.-]+)"',(BASE / 'persistent-diagnostic-history-173.h').read_text())
    assert len(names) == len(set(names)) == 13
    source = runpy.run_path(str(BASE / 'verify-persistent-data-166.py'))['PAYLOAD']
    anchor = ' result=dict(native_boot_id=boot'
    assert source.count(anchor) == 1
    extra = ''' extra_history={}
 for name in extra_names:
  text=command(['debugfs','-R','stat /.harmony-persistent166/'+boot+'/'+name,str(data)])
  present='Inode:' in text
  if present:assert ('Type: FIFO' in text if name.endswith('.fifo') else 'Type: regular' in text)
  extra_history[name]=present
 assert extra_history['commercial-collaboration-ready116.log']
 files=sum(present for name,present in extra_history.items() if not name.endswith('.fifo'))
 fifos=sum(present for name,present in extra_history.items() if name.endswith('.fifo'))
 assert files==expected_extra_files and fifos==expected_extra_fifos
'''
    source = source.replace(anchor,extra + anchor,1)
    anchor = "result['lab_partition_unmounted']=True"
    source = source.replace(anchor,"result['extra_diagnostic_history']=extra_history\n" + anchor,1)
    prefix = dict(number='173',expected_uuid=analysis['filesystem_uuid'],
        expected_boot=analysis['native_boot_id'],previous_boot=analysis['previous_native_boot_id'],
        expected_archived=5,require_memory_archive=True,extra_names=names,
        expected_extra_files=analysis['extra_diagnostic_files_archived'],
        expected_extra_fifos=analysis['extra_diagnostic_fifos_archived'])
    script = ''.join(key + '=' + repr(value) + '\n' for key,value in prefix.items()) + source
    compile(script,'persistent-data-verification173-remote','exec')
    runpy.run_path(str(BASE / 'commercial-workflow-173.py'))['configure_local_transport']()
    proc = subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','HostKeyAlias=192.168.10.128','zoinve@192.168.10.128','sudo -n python3 -'],
        input=script,capture_output=True,text=True,timeout=240)
    (REPORT / 'persistent-offline-verification.stdout').open('x').write(proc.stdout)
    (REPORT / 'persistent-offline-verification.stderr').open('x').write(proc.stderr)
    assert proc.returncode == 0,proc.stderr
    result = json.loads(proc.stdout)
    result.update(original_init_handoff_verified=True,full_native_storage_acceptance=True,
        repeated_successful_boots_verified=False,physical_desktop_interaction_verified=False)
    (REPORT / 'persistent-offline-verification.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
