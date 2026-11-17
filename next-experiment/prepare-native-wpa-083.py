"""Capture original supplicant/CLI dependencies without reading credentials."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
previous = runpy.run_path(str(Path(__file__).with_name('prepare-native-iw-082.py')))
REMOTE = previous['REMOTE'].replace("tool = Path('/usr/sbin/iw')", "tool = Path('/usr/sbin/wpa_supplicant')")
REMOTE = REMOTE.replace("['ldd', str(tool)]", "['ldd', str(tool), '/usr/sbin/wpa_cli']")
REMOTE = REMOTE.replace('paths = {str(tool.resolve())}', "paths = {str(tool.resolve()), '/usr/sbin/wpa_cli'}")
STAGE = previous['STAGE'].replace('native-iw-082', 'native-wpa-083')


def main():
    output = ROOT / 'reports/commercial-network-inputs-audit-083/wpa-stage.json'
    assert not output.exists(), 'preserve numbered evidence'
    args = ['ssh', '-i', 'C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
            '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
            '-o', 'ConnectTimeout=10', 'matebook', 'python3 -']
    remote = subprocess.run(args, input=REMOTE, text=True, capture_output=True, timeout=60, check=True)
    staged = subprocess.run(['wsl.exe', '-d', 'Debian', '--', 'python3', '-c', STAGE],
                            input=json.dumps(json.loads(remote.stdout)), text=True,
                            capture_output=True, timeout=90, check=True)
    result = json.loads(staged.stdout)
    assert not result['credentials_read'] and not result['ubuntu_network_modified']
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
