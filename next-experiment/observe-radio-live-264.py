"""Observe radio262's original read-only endpoint without repeating Settings tests."""
from pathlib import Path
import datetime
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/commercial61-native-262'


if __name__ == '__main__':
    output = REPORT / 'radio-live-observation-264.json'
    assert not output.exists()
    known = REPORT / 'native-known_hosts'
    key = json.loads((ROOT / 'reports/live-debug-inputs-157/result.json').read_text())['host_public_key']
    known.open('x').write('harmony-native-262 ' + key + '\n')
    client = ['ssh', '-i', 'C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
        '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
        '-o', 'HostKeyAlias=harmony-native-262', '-o', 'UserKnownHostsFile=' + str(known),
        '-o', 'ConnectTimeout=2', '-o', 'ConnectionAttempts=1', '-p', '22257']
    stamp = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = dict(start_utc=stamp(), authenticated_native_connected=False,
        bluetooth_enable_verified=False, wifi_ui_scan_verified=False,
        device_info_ui_verified=False, new_boot_requested=False, arbitrary_commands_executed=False)
    deadline = time.monotonic() + 120
    attempts = 0
    while time.monotonic() < deadline:
        attempts += 1
        proc = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-File', str(ROOT / 'next-experiment/discover-live-debug-159.ps1'),
            '-DurationSeconds', '4'], capture_output=True, timeout=15)
        if proc.returncode: continue
        endpoints = json.loads(proc.stdout.decode('utf-8-sig'))['endpoints']
        if len(endpoints) != 1: continue
        endpoint = endpoints[0]
        assert endpoint['port'] == 22257
        status = subprocess.run(client + ['root@' + endpoint['address'], 'status'],
            capture_output=True, text=True, timeout=10)
        if status.returncode: continue
        rows = [json.loads(line) for line in status.stdout.splitlines()]
        assert len(rows) == 3 and rows[0]['log'] == 'hilog' and rows[0]['available']
        result.update(authenticated_native_connected=True, endpoint=endpoint['address'],
                      connected_utc=stamp(), read_only_status=rows)
        break
    result.update(discovery_attempts=attempts, end_utc=stamp())
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
