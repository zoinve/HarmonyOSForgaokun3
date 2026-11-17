"""Record stopped-fixture and unchanged-source checks without restarting it."""
from pathlib import Path
import hashlib
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = r'''
from pathlib import Path
import hashlib,json,socket,subprocess
root=Path(REMOTE_ROOT)
record=json.loads((root/'preparation.json').read_text())
checks=[]
for row in record['files']:
 source=hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()
 staged=hashlib.sha256((root/'root'/row['path'].lstrip('/')).read_bytes()).hexdigest()
 assert source==staged==row['sha256'],row['path']
 checks.append(row['path'])
reader=hashlib.sha256((root/'root/bin/diag').read_bytes()).hexdigest()
assert reader==record['reader_sha256']
with socket.socket() as probe:
 probe.settimeout(.5)
 assert probe.connect_ex(('127.0.0.1',22256))!=0
supervisor=json.loads((root/'supervisor.json').read_text())
path=Path('/proc')/str(supervisor['pid'])
same_process=path.exists() and (path/'stat').read_text().split()[21]==supervisor['starttime']
if same_process:
 assert (path/'stat').read_text().split()[2]=='Z','fixture supervisor is still live'
timers=subprocess.run(['systemctl','list-timers','--all','--no-pager','--plain'],capture_output=True,text=True,check=True)
boot=subprocess.run(['bootctl','status','--no-pager'],capture_output=True,text=True,check=True)
print(json.dumps(dict(source_and_staged_binary_hashes_matched=checks,
 reader_sha256=reader,loopback_listener_absent=True,fixture_supervisor_running=False,
 ubuntu_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 ubuntu_kernel=subprocess.check_output(['uname','-r'],text=True).strip(),
 bootctl_status=boot.stdout,screenoff_timers=[line for line in timers.stdout.splitlines() if 'screen' in line.lower()],
 existing_ssh_service_active=subprocess.run(['systemctl','is-active','ssh.service'],capture_output=True,text=True).stdout.strip(),
 private_keys_read_or_exported=False,readonly_verification=True)))
'''


if __name__ == '__main__':
    output = ROOT / 'reports/live-debug-156/post-fixture-verification.json'
    assert not output.exists()
    remote = runpy.run_path(str(Path(__file__).with_name('prepare-live-debug-156.py')))['remote']
    result = remote(PAYLOAD)
    assert result['ubuntu_boot_id'] == '6643a37b-af4b-4656-af53-d6538bdf93b7'
    assert result['existing_ssh_service_active'] == 'active'
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(source_binary_count=len(result['source_and_staged_binary_hashes_matched']),
        loopback_listener_absent=result['loopback_listener_absent'],
        ubuntu_boot_id=result['ubuntu_boot_id'],existing_ssh_service_active=result['existing_ssh_service_active'],
        screenoff_timers=result['screenoff_timers']),indent=2))
