"""Essential identity/default-boot/timer checks, never disk validation suites."""
from pathlib import Path
import json
import runpy

ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 report=ROOT/'reports/commercial61-native-353'
 output=report/'post-return-guard-358.json';assert not output.exists()
 observed=json.loads((report/'boot-observation-355.json').read_text())
 assert observed['returned']
 boot=observed['ubuntu']['boot_id']
 module=runpy.run_path(str(ROOT/'next-experiment/settings-workflow-254.py'))
 check=module['GUARD']+'\nassert Path(\'/proc/sys/kernel/random/boot_id\').read_text().strip()=='+repr(boot)+'\n'
 check+='print(json.dumps(dict(boot_id='+repr(boot)+',ubuntu_current_and_default=True,oneshot_absent=True,screenoff_timer_enabled_active=True,lab_identity_verified=True,lab_partition_unmounted=True,disk_hash_fsck_tree_suites_run=False)))\n'
 result=module['remote'](check)
 json.loads(result);output.open('x').write(result)
 print(result)
