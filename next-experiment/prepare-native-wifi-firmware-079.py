"""Copy existing board Wi-Fi firmware read-only to a fresh WSL workspace."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REMOTE = r'''
from pathlib import Path
import base64, hashlib, json, subprocess
base = Path('/usr/lib/firmware')
wifi = base / 'ath11k/WCN6855'
rows = []
assert wifi.is_dir()
paths = sorted(wifi.rglob('*')) + [base / 'regulatory.db', base / 'regulatory.db.p7s']
for path in paths:
    if not path.exists():
        continue
    relative = str(path.relative_to(base))
    if path.is_symlink():
        assert path.resolve().is_relative_to(base.resolve())
        rows.append(dict(path=relative, kind='symlink', target=str(path.readlink())))
    elif path.is_file():
        blob = path.read_bytes()
        rows.append(dict(path=relative, kind='file', bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(), data=base64.b64encode(blob).decode()))
iface = Path('/sys/class/net/wlP6p1s0')
device = iface / 'device'
identity = {key: (device / key).read_text().strip() for key in ('vendor', 'device', 'subsystem_vendor', 'subsystem_device')}
log = subprocess.run(['sudo', '-n', 'dmesg'], capture_output=True, text=True, check=True).stdout
selected = [line for line in log.splitlines() if any(x in line.lower() for x in ('ath11k', 'wcn6855', 'cfg80211', 'regulatory.db'))]
print(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(), kernel=subprocess.check_output(['uname','-r'], text=True).strip(), driver=str((device / 'driver').resolve()), identity=identity, kernel_network_log=selected, firmware=rows, ubuntu_modified=False)))
'''
STAGE = r'''
from pathlib import Path
import base64, hashlib, json, sys
record = json.load(sys.stdin)
root = Path('/home/zoinve/harmony-virgl-883/native-wifi-firmware-079')
root.mkdir(exist_ok=False)
for row in record['firmware']:
    relative = Path(row['path'])
    assert not relative.is_absolute() and '..' not in relative.parts
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if row['kind'] == 'symlink':
        assert not Path(row['target']).is_absolute() and '..' not in Path(row['target']).parts
        target.symlink_to(row['target'])
    else:
        blob = base64.b64decode(row.pop('data'), validate=True)
        assert len(blob) == row['bytes'] and hashlib.sha256(blob).hexdigest() == row['sha256']
        with target.open('xb') as stream:
            stream.write(blob)
for row in record['firmware']:
    target = root / row['path']
    assert target.exists()
    if row['kind'] == 'file':
        assert hashlib.sha256(target.read_bytes()).hexdigest() == row['sha256']
record.update(stage=str(root), target_rebooted=False, network_configuration_read=False, network_configuration_modified=False)
with (root / 'result.json').open('x') as stream:
    json.dump(record, stream, indent=2)
print(json.dumps(record, indent=2))
'''


def main():
    args = ['ssh', '-i', 'C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
            '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
            '-o', 'ConnectTimeout=10', 'matebook', 'python3 -']
    remote = subprocess.run(args, input=REMOTE, text=True, capture_output=True, timeout=60, check=True)
    record = json.loads(remote.stdout)
    staged = subprocess.run(['wsl.exe', '-d', 'Debian', '--', 'python3', '-c', STAGE],
                            input=json.dumps(record), text=True, capture_output=True, timeout=90, check=True)
    result = json.loads(staged.stdout)
    output = ROOT / 'reports/commercial-network-inputs-audit-079/firmware-stage.json'
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
