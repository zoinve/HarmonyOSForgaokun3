"""Read-only capture of Ubuntu's iw and its original dynamic dependencies."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REMOTE = r'''
from pathlib import Path
import base64, hashlib, json, re, subprocess
tool = Path('/usr/sbin/iw')
result = subprocess.run(['ldd', str(tool)], capture_output=True, text=True, check=True)
assert 'not found' not in result.stdout
paths = {str(tool.resolve())}
for line in result.stdout.splitlines():
    match = re.search(r'(?:=>\s+)?(/\S+)\s+\(0x[0-9a-f]+\)', line)
    if match:
        paths.add(match.group(1))
assert '/lib/ld-linux-aarch64.so.1' in paths
rows = []
for name in sorted(paths):
    path = Path(name)
    assert path.is_absolute() and path.is_file()
    blob = path.read_bytes()
    assert blob[:4] == b'\x7fELF'
    assert int.from_bytes(blob[18:20], 'little') == 183
    rows.append(dict(path=name, resolved=str(path.resolve()), bytes=len(blob),
                     sha256=hashlib.sha256(blob).hexdigest(), data=base64.b64encode(blob).decode()))
version = subprocess.check_output([str(tool), '--version'], text=True).strip()
print(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
    version=version, ldd_stdout=result.stdout, files=rows,
    credentials_read=False, ubuntu_network_modified=False)))
'''
STAGE = r'''
from pathlib import Path
import base64, hashlib, json, sys
record = json.load(sys.stdin)
root = Path('/home/zoinve/harmony-virgl-883/native-iw-082')
root.mkdir(exist_ok=False)
for row in record['files']:
    name = Path(row['path'])
    assert name.is_absolute() and '..' not in name.parts
    target = root / str(name).lstrip('/')
    target.parent.mkdir(parents=True, exist_ok=True)
    blob = base64.b64decode(row.pop('data'), validate=True)
    assert len(blob) == row['bytes']
    assert hashlib.sha256(blob).hexdigest() == row['sha256']
    with target.open('xb') as stream:
        stream.write(blob)
    target.chmod(0o755)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == row['sha256']
record['stage'] = str(root)
with (root / 'result.json').open('x') as stream:
    json.dump(record, stream, indent=2)
print(json.dumps(record, indent=2))
'''


def main():
    output = ROOT / 'reports/commercial-network-inputs-audit-082/iw-stage.json'
    assert not output.exists(), 'preserve numbered evidence'
    args = ['ssh', '-i', 'C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
            '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
            '-o', 'ConnectTimeout=10', 'matebook', 'python3 -']
    remote = subprocess.run(args, input=REMOTE, text=True, capture_output=True,
                            timeout=60, check=True)
    record = json.loads(remote.stdout)
    staged = subprocess.run(['wsl.exe', '-d', 'Debian', '--', 'python3', '-c', STAGE],
                            input=json.dumps(record), text=True, capture_output=True,
                            timeout=90, check=True)
    result = json.loads(staged.stdout)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
