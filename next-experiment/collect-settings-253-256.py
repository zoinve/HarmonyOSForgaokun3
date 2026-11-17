"""Observe this boot's Ubuntu return and collect logs without storage test suites."""
from pathlib import Path
import datetime
import json
import runpy
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-253'
SSH = runpy.run_path(str(BASE / 'deploy-settings-data-198.py'))['SSH']


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['observe', 'retrieve']
    observation = REPORT / 'boot-observation-256.json'
    if sys.argv[1] == 'observe':
        if observation.exists():
            print(observation.read_text())
        else:
            query = "from pathlib import Path;import json,subprocess;print(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),release=subprocess.check_output(['uname','-r'],text=True).strip())))"
            proc = subprocess.run(SSH + ['python3 -'], input=query, text=True, capture_output=True, timeout=15)
            if proc.returncode:
                print(json.dumps(dict(ubuntu_observed=False,ssh_exit=proc.returncode,new_boot_requested=False)))
                raise SystemExit(0)
            state = json.loads(proc.stdout)
            attempt = json.loads((REPORT / 'boot-attempt.json').read_text())
            if state['boot_id'] == attempt['before_boot_id']:
                print(json.dumps(dict(ubuntu_observed=True,return_observed=False,new_boot_requested=False)))
                raise SystemExit(0)
            assert state['release'] == '7.1.0-rc3-gaokun3+'
            result = dict(returned=True,ubuntu=state,
                observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                reboot_cause_not_proven_by_observation=True,settings_window_verified=False,
                filesystem_validation_suite_rerun=False,new_boot_requested=False)
            observation.open('x').write(json.dumps(result, indent=2))
            print(json.dumps(result, indent=2))
    else:
        assert json.loads(observation.read_text())['returned']
        source = (ROOT / 'reports/commercial61-native-235/readable-retrieval-241.generated.py').read_text()
        source = source.replace('commercial61-native-235', 'commercial61-native-253')
        source = source.replace('commercial-return-audit-235', 'commercial-return-audit-253')
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        prior = json.loads((ROOT / 'reports/commercial61-native-235/runtime-evidence-recovered-247/retrieval-manifest.json').read_text())['run']
        source = source.replace(anchor, anchor + repr(prior) + ', ', 1)
        old = "manifest['unreadable_directory_entry_observed']='phase-207.log'\n"
        assert source.count(old) == 1
        source = source.replace(old, '', 1)
        old = "manifest['complete_directory_export']=False"
        source = source.replace(old, "manifest['standard_desktop_snapshot_not_required']=True\nmanifest['full_experiment_completion_not_inferred']=True", 1)
        compile(source, 'retrieve253-256', 'exec')
        (REPORT / 'retrieve-256.generated.py').open('x').write(source)
        runpy.run_path(str(BASE / 'commercial-workflow-235.py'))['configure_local_transport']()
        exec(compile(source, 'retrieve253-256', 'exec'),
             {'__name__': '__main__', '__file__': str(BASE / 'retrieve253-256.py')})
