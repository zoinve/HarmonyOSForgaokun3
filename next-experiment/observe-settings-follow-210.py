"""Bounded read-only follow of the already authenticated206 endpoint."""
from pathlib import Path
import datetime
import json
import subprocess
import time

ROOT=Path(__file__).resolve().parent.parent
REPORT=ROOT/'reports/commercial61-native-206'


def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    output=REPORT/'live-follow-210.json';assert not output.exists()
    first=json.loads((REPORT/'live-client-observation.json').read_text())
    assert first['discovered_endpoint_pinned_ssh_authenticated']
    endpoint=first['connected_address']
    client=['ssh','-i','C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
        '-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','HostKeyAlias=harmony-native-206','-o','UserKnownHostsFile='+str(REPORT/'native-known_hosts'),
        '-o','ConnectTimeout=3','-o','ConnectionAttempts=1','-p','22257','root@'+endpoint]
    record=dict(start_utc=stamp(),observations=[],target_modified=False,boot_requested=False,
        full_debugger_attached=False,settings_window_verified=False)
    try:
        for index in range(4):
            if index:time.sleep(90)
            snapshot=dict(utc=stamp(),index=index,commands=[])
            for command in ['status','settings','follow-settings']:
                proc=subprocess.run(client+[command],capture_output=True,text=True,timeout=40)
                row=dict(command=command,returncode=proc.returncode)
                if proc.returncode==0:
                    messages=[json.loads(line) for line in proc.stdout.splitlines()]
                    if command=='status':row['log_status']=messages
                    else:
                        row['event_counts']={name:sum(item.get('event')==name for item in messages)
                            for name in sorted({item.get('event','unnamed') for item in messages})}
                snapshot['commands'].append(row)
                if proc.returncode:break
            record['observations'].append(snapshot)
            print(json.dumps(snapshot),flush=True)
            if any(item['returncode'] for item in snapshot['commands']):break
    finally:
        record['end_utc']=stamp()
        with output.open('x') as stream:json.dump(record,stream,indent=2)


if __name__=='__main__':main()
