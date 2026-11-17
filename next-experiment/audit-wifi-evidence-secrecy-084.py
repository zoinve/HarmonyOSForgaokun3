"""Compare evidence token digests on-device; never retrieve the private PSK."""
from pathlib import Path
import hashlib
import json
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REMOTE = r'''
from pathlib import Path
import hashlib, json, re, sys
request=json.load(sys.stdin)
path=Path.home()/'.local/share/harmony-arm64-kvm-lab/native-wpa-connection-084/wpa.conf'
body=path.read_bytes()
assert hashlib.sha256(body).hexdigest()==request['expected_config_sha256']
match=re.search(rb'^\s*psk=([a-f0-9]{64})$',body,re.M)
assert match
digest=hashlib.sha256(match.group(1).lower()).hexdigest()
print(json.dumps(dict(config_hash_verified=True,credential_value_found_in_evidence=digest in request['candidate_digests'],
 credential_exported=False,comparison_scope='exact_64_hex_psk_value_in_retrieved_bytes')))
'''


def main():
    output = ROOT / 'reports/commercial61-native-084/evidence-secrecy-audit.json'
    assert not output.exists()
    folder = output.parent / 'runtime-evidence/raw'
    files = sorted(path for path in folder.iterdir() if path.is_file())
    assert files
    tokens, total = set(), 0
    pattern = re.compile(rb'[0-9a-fA-F]{64}')
    for path in files:
        tail = b''
        with path.open('rb') as stream:
            while chunk := stream.read(1024 * 1024):
                total += len(chunk)
                data = tail + chunk
                for match in pattern.finditer(data):
                    tokens.add(hashlib.sha256(match.group().lower()).hexdigest())
                tail = data[-63:]
    config = json.loads((ROOT / 'reports/commercial-network-inputs-audit-084/connection-ready.json').read_text())
    request = dict(expected_config_sha256=config['sha256'], candidate_digests=sorted(tokens))
    args = ['ssh', '-i', 'C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
            '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
            '-o', 'ConnectTimeout=10', 'matebook', 'python3 -c ' + shlex.quote(REMOTE)]
    remote = subprocess.run(args, input=json.dumps(request), text=True, capture_output=True, timeout=45, check=True)
    result = json.loads(remote.stdout)
    result.update(files_scanned=len(files), bytes_scanned=total, unique_candidate_digests=len(tokens))
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
    assert not result['credential_value_found_in_evidence'], 'sensitive evidence requires isolation'
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
