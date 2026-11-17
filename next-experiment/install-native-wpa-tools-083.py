"""Install a new immutable experiment input in Ubuntu's user-owned lab directory."""
from pathlib import Path
import json
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = r'''
from pathlib import Path
import base64, hashlib, json
root=Path('/home/zoinve/harmony-virgl-883/native-wpa-package-083')
record=json.loads((root/'result.json').read_text())
blob=(root/'tools.tar.gz').read_bytes()
assert hashlib.sha256(blob).hexdigest()==record['sha256'] and len(blob)==record['bytes']
record['data']=base64.b64encode(blob).decode()
print(json.dumps(record))
'''
INSTALL = r'''
from pathlib import Path
import base64, hashlib, json, os, sys
record=json.load(sys.stdin)
root=Path.home()/'.local/share/harmony-arm64-kvm-lab/native-wpa-tools-083'
assert str(root/'tools.tar.gz')==record['destination']
root.mkdir(mode=0o700,exist_ok=False)
blob=base64.b64decode(record.pop('data'),validate=True)
assert len(blob)==record['bytes'] and hashlib.sha256(blob).hexdigest()==record['sha256']
with (root/'tools.tar.gz').open('xb') as stream:
    os.fchmod(stream.fileno(),0o400)
    stream.write(blob);stream.flush();os.fsync(stream.fileno())
assert hashlib.sha256((root/'tools.tar.gz').read_bytes()).hexdigest()==record['sha256']
record.update(ubuntu_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
              ubuntu_network_modified=False,original_images_written=False,esp_written=False)
with (root/'installation.json').open('x') as stream:
    json.dump(record,stream,indent=2);stream.flush();os.fsync(stream.fileno())
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps(record))
'''


def main():
    output = ROOT / 'reports/commercial-network-inputs-audit-083/tool-installation.json'
    assert not output.exists()
    capture = subprocess.run(['wsl.exe', '-d', 'Debian', '--', 'python3', '-c', CAPTURE],
                             capture_output=True, text=True, check=True, timeout=60)
    args = ['ssh', '-i', 'C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
            '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
            '-o', 'ConnectTimeout=10', 'matebook', 'python3 -c ' + shlex.quote(INSTALL)]
    installed = subprocess.run(args, input=capture.stdout, capture_output=True,
                               text=True, check=True, timeout=120)
    result = json.loads(installed.stdout)
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({key: result[key] for key in ('destination', 'bytes', 'sha256', 'ubuntu_boot_id', 'ubuntu_network_modified', 'original_images_written', 'esp_written')}, indent=2))


if __name__ == '__main__':
    main()
