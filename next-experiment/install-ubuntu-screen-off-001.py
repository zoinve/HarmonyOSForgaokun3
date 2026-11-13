"""Install only the new screen-off helper/timer; never reboot or modify boot entries."""
from pathlib import Path
import hashlib
import json
import subprocess

base = Path(__file__).resolve().parent
report = base.parent / 'reports/ubuntu-screen-off-001.json'
assert not report.exists()
artifacts = {
    '/usr/local/libexec/harmony-lab-screen-off-001.py': (base / 'ubuntu-screen-off-001.py').read_text(),
    '/etc/systemd/system/harmony-lab-screen-off-001.service': (base / 'harmony-lab-screen-off-001.service').read_text(),
    '/etc/systemd/system/harmony-lab-screen-off-001.timer': (base / 'harmony-lab-screen-off-001.timer').read_text(),
}
payload = 'artifacts = ' + repr(artifacts) + '\n' + r'''
from pathlib import Path
import hashlib,json,os,subprocess
assert os.uname().release=='7.1.0-rc3-gaokun3+'
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text().split()
assert not Path('/etc/harmony-lab-screen-off.disabled').exists()
for name in artifacts:assert not Path(name).exists(),name
def run(args):
    r=subprocess.run(args,capture_output=True,text=True,timeout=55)
    assert r.returncode==0,(args,r.returncode,r.stdout,r.stderr)
    return r.stdout.strip()
Path('/usr/local/libexec').mkdir(exist_ok=True)
for name,text in artifacts.items():
    p=Path(name)
    with p.open('x') as f:f.write(text)
    p.chmod(0o644)
run(['systemd-analyze','verify','/etc/systemd/system/harmony-lab-screen-off-001.service','/etc/systemd/system/harmony-lab-screen-off-001.timer'])
run(['systemctl','daemon-reload'])
run(['systemctl','enable','--now','harmony-lab-screen-off-001.timer'])
run(['systemctl','start','harmony-lab-screen-off-001.service'])
state=run(['systemctl','show','harmony-lab-screen-off-001.service','--property=Result,ExecMainStatus'])
assert 'Result=success' in state and 'ExecMainStatus=0' in state,state
assert run(['systemctl','is-enabled','harmony-lab-screen-off-001.timer'])=='enabled'
assert run(['systemctl','is-active','harmony-lab-screen-off-001.timer'])=='active'
namespace={'__name__':'screen_off_verification'}
exec(compile(artifacts['/usr/local/libexec/harmony-lab-screen-off-001.py'],'installed-screen-off','exec'),namespace)
rows=namespace['run_once']()
assert rows and all(row['state']=='off' for row in rows),rows
saved=Path('/run/harmony-lab-screen-off-001.json')
print(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
    installed=[dict(path=name,sha256=hashlib.sha256(Path(name).read_bytes()).hexdigest()) for name in artifacts],
    timer_enabled=True,timer_active=True,service_state=state,graphical_sessions=rows,
    original_backlight_settings=json.loads(saved.read_text()) if saved.exists() else None,
    reboot_requested=False,boot_entries_modified=False,physical_screen_observed=False)))
'''
result = subprocess.run(['ssh', '-o', 'ConnectTimeout=3', 'matebook', 'sudo -n python3 -'],
                        input=payload, text=True, capture_output=True, timeout=90)
assert result.returncode == 0, result.stderr or result.stdout
record = json.loads(result.stdout)
for row in record['installed']:
    assert row['sha256'] == hashlib.sha256(artifacts[row['path']].encode()).hexdigest()
report.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
