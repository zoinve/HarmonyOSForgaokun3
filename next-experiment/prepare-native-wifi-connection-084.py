"""Prepare an on-device private config; never transfer a credential to the repo."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REMOTE = r'''
from pathlib import Path
import hashlib, json, os, re, subprocess, uuid
def query(field, profile=None, secret=False):
    args=['nmcli','--escape','no','--get-values',field]
    args+=['connection','show',profile] if profile else ['device','show','wlP6p1s0']
    if secret: args=['sudo','-n']+args[:1]+['--show-secrets']+args[1:]
    output=subprocess.run(args,capture_output=True,check=True).stdout
    assert output.endswith(b'\n')
    output=output[:-1]
    assert b'\n' not in output and b'\r' not in output and b'\0' not in output
    return output
profile=query('GENERAL.CON-UUID').decode()
assert str(uuid.UUID(profile))==profile
assert query('802-11-wireless-security.key-mgmt',profile)==b'wpa-psk'
ssid=query('802-11-wireless.ssid',profile)
secret=query('802-11-wireless-security.psk',profile,True)
assert 1<=len(ssid)<=32
if re.fullmatch(b'[0-9a-fA-F]{64}',secret): key=secret.decode().lower()
else:
    assert 8<=len(secret)<=63
    key=hashlib.pbkdf2_hmac('sha1',secret,ssid,4096,32).hex()
body=('ctrl_interface=DIR=/data/local/tmp/wpa_ctrl GROUP=1010\nupdate_config=0\nap_scan=1\n'
      'network={\n    ssid='+ssid.hex()+'\n    psk='+key+'\n    key_mgmt=WPA-PSK\n    ieee80211w=1\n}\n').encode()
root=Path.home()/'.local/share/harmony-arm64-kvm-lab/native-wpa-connection-084'
root.mkdir(mode=0o700,exist_ok=False)
with (root/'wpa.conf').open('xb') as stream:
    os.fchmod(stream.fileno(),0o400);stream.write(body);stream.flush();os.fsync(stream.fileno())
assert hashlib.sha256((root/'wpa.conf').read_bytes()).digest()==hashlib.sha256(body).digest()
result=dict(destination=str(root/'wpa.conf'),bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),
 ubuntu_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 active_profile_uuid=profile,original_ubuntu_network_modified=False,credential_exported=False,
 credential_read_on_device=True,configuration_ready=True,key_management='WPA-PSK',
 file_mode=oct((root/'wpa.conf').stat().st_mode & 0o777),parent_mode=oct(root.stat().st_mode & 0o777))
with (root/'provenance.json').open('x') as stream:
    json.dump(result,stream,indent=2);stream.flush();os.fsync(stream.fileno())
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps(result))
'''


def main():
    output = ROOT / 'reports/commercial-network-inputs-audit-084/connection-ready.json'
    assert not output.exists()
    args = ['ssh', '-i', 'C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
            '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
            '-o', 'ConnectTimeout=10', 'matebook', 'python3 -']
    remote = subprocess.run(args, input=REMOTE, text=True, capture_output=True, timeout=45, check=True)
    result = json.loads(remote.stdout)
    assert not result['credential_exported'] and result['configuration_ready']
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
