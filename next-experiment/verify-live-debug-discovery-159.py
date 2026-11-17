"""One bounded Ubuntu network fixture; preserve all existing numbered runs."""
from pathlib import Path
import base64
import hashlib
import json
import select
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'next-experiment'
assert sys.argv[1:] in [[], ['--compile-fix-1']], 'explicit immutable attempt only'
SUFFIX = '-compile-fix-1' if sys.argv[1:] else ''
REPORT = ROOT / ('reports/live-debug-discovery-159' + SUFFIX)
BUILD = Path('/home/zoinve/harmony-virgl-883/live-debug-discovery-159' + SUFFIX)
REMOTE = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-discovery-159' + SUFFIX
SSH = ['/mnt/c/Windows/System32/OpenSSH/ssh.exe', '-i',
       'C:/Users/39255/.ssh/id_ed25519_opencode_matebook', '-o', 'BatchMode=yes',
       '-o', 'StrictHostKeyChecking=yes', '-o', 'HostKeyAlias=192.168.10.128',
       '-o', 'ConnectTimeout=8', 'zoinve@192.168.10.128']

REMOTE_RUN = r'''
from pathlib import Path
import base64,hashlib,json,os,subprocess
root=Path(REMOTE_ROOT)
assert os.geteuid()==0 and not root.exists()
def snapshot():
 data=json.loads(subprocess.check_output(['ip','-j','-4','address'],text=True))
 addresses=[(i['ifname'],a['local'],a['prefixlen']) for i in data for a in i['addr_info']]
 return dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),addresses=addresses,
  routes=json.loads(subprocess.check_output(['ip','-j','-4','route'],text=True)),
  ssh_config_sha256=hashlib.sha256(Path('/etc/ssh/sshd_config').read_bytes()).hexdigest(),
  ssh_active=subprocess.check_output(['systemctl','is-active','ssh'],text=True).strip())
before=snapshot()
root.mkdir(mode=0o700)
binary=base64.b64decode(BINARY_BASE64,validate=True)
assert hashlib.sha256(binary).hexdigest()==BINARY_SHA256
target=root/'fixture'
target.write_bytes(binary);target.chmod(0o700)
run=subprocess.run(['/usr/bin/timeout','--signal=TERM','--kill-after=2','20',str(target),'--ubuntu-fixture','192.168.10.128'])
after=snapshot()
listener=subprocess.check_output(['ss','-H','-u','-l','-n','sport = :22259'],text=True).strip()
result=dict(fixture_only=True,harmony_boot_performed=False,ssh_authentication_proved=False,
 returncode=run.returncode,before=before,after=after,preservation_pass=before==after,listener_absent=not listener,
 binary_sha256=BINARY_SHA256,firewall_or_network_configuration_changed=False)
(root/'result.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(result),flush=True)
assert run.returncode==0 and before==after and not listener
'''


def main():
    assert not REPORT.exists() and not BUILD.exists(), 'preserve numbered evidence'
    REPORT.mkdir()
    BUILD.mkdir()
    for name in ['address', 'discovery']:
        test = subprocess.run(['python3', str(BASE / f'test-live-debug-{name}-159.py')], capture_output=True, timeout=20)
        (REPORT / f'{name}-tests.stderr').open('xb').write(test.stderr)
        assert test.returncode == 0, test.stderr.decode()
    binary = BUILD / 'fixture'
    compiled = subprocess.run(['aarch64-linux-gnu-gcc', '-static', '-Os', '-s', '-Wall', '-Wextra', '-Werror',
        str(BASE / 'live-debug-discovery-fixture-159.c'), '-o', str(binary)], capture_output=True, timeout=60)
    (REPORT / 'compile.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr.decode()
    data = binary.read_bytes()
    source = REMOTE_RUN.replace('REMOTE_ROOT', repr(REMOTE)).replace('BINARY_BASE64', repr(base64.b64encode(data).decode())).replace('BINARY_SHA256', repr(hashlib.sha256(data).hexdigest()))
    process = subprocess.Popen([*SSH, 'sudo -n python3 -'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    process.stdin.write(source)
    process.stdin.close()
    process.stdin = None
    first = ''
    clients = []
    try:
        assert select.select([process.stdout], [], [], 12)[0], 'no fixture readiness'
        first = process.stdout.readline()
        assert first.startswith('UBUNTU_ONLY_DISCOVERY159_READY '), first
        script = subprocess.check_output(['wslpath', '-w', str(BASE / 'discover-live-debug-159.ps1')], text=True).strip()
        for negative, seconds in [(True, 2), (False, 6)]:
            command = ['/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script, '-DurationSeconds', str(seconds)]
            if negative:
                command.append('-MalformedOnly')
            result = subprocess.run(command, capture_output=True, timeout=seconds + 10)
            text = result.stdout.decode('utf-8-sig').strip()
            record = dict(negative=negative, returncode=result.returncode, result=json.loads(text), stderr=result.stderr.decode('utf-8', errors='replace'))
            clients.append(record)
            (REPORT / ('negative-client.json' if negative else 'client.json')).open('x').write(json.dumps(record, indent=2))
    finally:
        # The remote supervisor owns its 20-second deadline even on client errors.
        stdout, stderr = process.communicate(timeout=30)
        (REPORT / 'remote.stdout').open('x').write(first + stdout)
        (REPORT / 'remote.stderr').open('x').write(stderr)
    remote = json.loads(stdout.splitlines()[-1])
    passed = process.returncode == 0 and len(clients) == 2 and all(row['returncode'] == 0 for row in clients)
    if passed:
        endpoints = clients[1]['result']['endpoints']
        passed = len(endpoints) == 1 and endpoints[0]['address'] == '192.168.10.128' and remote['preservation_pass'] and remote['listener_absent']
    result = dict(network_discovery_fixture_pass=passed, fixture_only=True, harmony_live_connection_verified=False,
        ssh_authentication_verified=False, remote=remote, clients=clients,
        sources={name:hashlib.sha256((BASE / name).read_bytes()).hexdigest() for name in
            ['live-debug-discovery-159.h','live-debug-discovery-fixture-159.c','discover-live-debug-159.ps1']})
    (REPORT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    assert passed, 'inspect immutable fixture evidence before deciding next action'


if __name__ == '__main__':
    main()
