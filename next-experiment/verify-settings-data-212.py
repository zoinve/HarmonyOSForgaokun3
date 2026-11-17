"""Read-only206 disk audit after207's transport refusal; never repair/replay."""
from pathlib import Path
import json
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REPORT=ROOT/'reports/commercial61-native-206'


if __name__=='__main__':
    output=REPORT/'settings-data-offline-212.json';assert not output.exists()
    analysis=json.loads((REPORT/'settings-persistent-analysis-207.json').read_text())
    assert analysis['all_retrieved_hashes_verified']
    provision=json.loads((ROOT/'reports/settings-data-deploy-198-r3/provision.json').read_text())
    payload=runpy.run_path(str(BASE/'verify-settings-data-199.py'))['PAYLOAD']
    payload=payload.replace('/mnt/settings199-offline','/mnt/settings212-offline')
    code='expected_active='+repr(provision['active165_before_sha256'])+'\nexpected_boot='+repr(analysis['native_boot_id'])+'\n'+payload
    compile(code,'settings212-remote','exec')
    ssh=runpy.run_path(str(BASE/'deploy-settings-data-198.py'))['SSH']
    proc=subprocess.run(ssh+['sudo -n python3 -'],input=code,text=True,capture_output=True,timeout=300)
    for suffix,data in [('stdout',proc.stdout),('stderr',proc.stderr)]:
        (REPORT/('settings-data-offline-212.'+suffix)).open('x').write(data)
    assert proc.returncode==0,proc.stderr
    result=json.loads(proc.stdout)
    result['native_teardown_verified']=analysis['native_disk_mount_and_flush_verified']
    result['full_native_storage_acceptance']=all([result['native_teardown_verified'],
        result['filesystem_clean'],result['disk_marker_matches_native_runtime']])
    result['prior207_remote_query_refused_before_disk_access']=True
    output.open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
