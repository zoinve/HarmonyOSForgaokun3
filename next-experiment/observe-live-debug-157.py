"""Observe only the single planned native boot through a pinned SSH host key."""
from pathlib import Path
import datetime
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/commercial61-native-157'
SSH = '/mnt/c/Windows/System32/OpenSSH/ssh.exe'


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


if __name__ == '__main__':
    output = REPORT / 'live-client-observation.json'
    assert not output.exists()
    package = json.loads((ROOT / 'reports/live-debug-inputs-157/result.json').read_text())
    known = REPORT / 'native-known_hosts'
    known.open('x').write('harmony-native-157 ' + package['host_public_key'] + '\n')
    known_windows = subprocess.check_output(['wslpath','-w',str(known)],text=True).strip()
    client = [SSH,'-i','C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
        '-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','HostKeyAlias=harmony-native-157','-o','UserKnownHostsFile='+known_windows,
        '-o','ConnectTimeout=2','-o','ConnectionAttempts=1','-p','22257','root@192.168.10.210']
    record = dict(start_utc=stamp(),attempts=[],authenticated_native_candidate_connected=False,
        native_namespace_identity_pending_evidence=True,full_process_debugger_attached=False,
        raw_logs_or_input_events_exported=False,boot_requested_by_this_observer=False)
    deadline = time.monotonic() + 270
    def query(command, timeout=10):
        completed = subprocess.run([*client,command],capture_output=True,text=True,timeout=timeout)
        return dict(command=command,utc=stamp(),returncode=completed.returncode,
            stderr=completed.stderr[:2000],stdout=completed.stdout)
    try:
        while time.monotonic() < deadline:
            attempted = query('status')
            record['attempts'].append({key:attempted[key] for key in ['utc','returncode','stderr']})
            if attempted['returncode'] == 0:
                rows = [json.loads(line) for line in attempted['stdout'].splitlines()]
                assert len(rows) == 3 and rows[0]['log'] == 'hilog' and rows[0]['available']
                assert rows[1]['log'] == 'native' and rows[1]['available']
                record.update(authenticated_native_candidate_connected=True,status_before=rows,connected_utc=stamp())
                break
            time.sleep(2)
        if record['authenticated_native_candidate_connected']:
            record['settings_snapshot'] = query('settings')
            assert record['settings_snapshot']['returncode'] == 0
            record['settings_follow'] = query('follow-settings',40)
            assert record['settings_follow']['returncode'] == 0
            events = [json.loads(line)['event'] for line in record['settings_follow']['stdout'].splitlines()]
            assert events[0] == 'following_settings' and events[-1] == 'settings_read_complete'
            record['status_after'] = [json.loads(line) for line in query('status')['stdout'].splitlines()]
            record['hilog_grew_during_connection'] = record['status_after'][0]['bytes'] > record['status_before'][0]['bytes']
            rejected = query('sh')
            assert rejected['returncode'] == 77 and 'command_refused' in rejected['stderr']
            record['arbitrary_shell_refused'] = True
            record['live_follow_protocol_completed'] = True
    except Exception as error:
        record['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        record['end_utc'] = stamp()
        output.open('x').write(json.dumps(record,indent=2))
        print(json.dumps({key:record.get(key) for key in ['authenticated_native_candidate_connected',
            'hilog_grew_during_connection','live_follow_protocol_completed','arbitrary_shell_refused','error','end_utc']},indent=2))
