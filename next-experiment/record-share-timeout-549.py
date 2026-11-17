"""Record current connectivity after532's terminal observation timeout; no reboot."""
from pathlib import Path
import datetime
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports/commercial61-native-532'

if __name__ == '__main__':
    output=REPORT/'connectivity-after-timeout-549.json'
    assert not output.exists()
    attempt=json.loads((REPORT/'boot-attempt.json').read_text())
    assert attempt['attempt_count']==1
    prior=json.loads((REPORT/'radio-live-observation-541.json').read_text())
    observe=subprocess.run([sys.executable,str(ROOT/'next-experiment/collect-share-532-536.py'),'observe'],
                           capture_output=True,text=True,timeout=30)
    command=['ssh','-i','C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
        '-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','HostKeyAlias=harmony-native-532','-o','UserKnownHostsFile='+str(REPORT/'native-known_hosts'),
        '-o','ConnectTimeout=3','-o','ConnectionAttempts=1','-p','22257','root@'+prior['endpoint'],'status']
    native=subprocess.run(command,capture_output=True,text=True,timeout=10)
    discovery=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',
        str(ROOT/'next-experiment/discover-live-debug-159.ps1'),'-DurationSeconds','4'],
        capture_output=True,timeout=15)
    discovery_result=json.loads(discovery.stdout.decode('utf-8-sig'))
    observation=REPORT/'boot-observation-536.json'
    returned=observation.exists() and json.loads(observation.read_text()).get('returned',False)
    result=dict(observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                prior_waiter_537_observation_expired=True,ubuntu_observed_now=bool(returned),
                observe_exit=observe.returncode,observe_output=observe.stdout.strip(),
                native_status_exit=native.returncode,
                native_status=None if native.returncode else [json.loads(x) for x in native.stdout.splitlines()],
                discovery_exit=discovery.returncode,discovered_endpoints=discovery_result['endpoints'],
                reboot_cause_or_current_screen_not_proven=True,new_boot_requested=False,
                file_transfer_verified=False)
    with output.open('x') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(result,indent=2))
