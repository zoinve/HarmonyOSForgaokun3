"""Read only non-secret properties needed for the next real association."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REMOTE = r'''
from pathlib import Path
import json, subprocess, uuid
def query(*args):
    return subprocess.run(['nmcli','--get-values',*args],capture_output=True,text=True,check=True).stdout.strip()
profile=query('GENERAL.CON-UUID','device','show','wlP6p1s0')
assert str(uuid.UUID(profile))==profile
fields=('connection.type','802-11-wireless.mode','802-11-wireless.band',
        '802-11-wireless-security.key-mgmt','802-11-wireless-security.psk-flags',
        '802-11-wireless-security.pmf','ipv4.method','ipv6.method')
properties={field:query(field,'connection','show',profile) for field in fields}
print(json.dumps(dict(ubuntu_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 active_profile_uuid=profile,interface='wlP6p1s0',nonsecret_properties=properties,
 credentials_read=False,ssid_read=False,ubuntu_network_modified=False)))
'''


def main():
    output = ROOT / 'reports/commercial-network-inputs-audit-084/active-profile.json'
    assert not output.exists()
    args = ['ssh', '-i', 'C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
            '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
            '-o', 'ConnectTimeout=10', 'matebook', 'python3 -']
    remote = subprocess.run(args, input=REMOTE, text=True, capture_output=True, timeout=45, check=True)
    result = json.loads(remote.stdout)
    output.parent.mkdir(exist_ok=True)
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
