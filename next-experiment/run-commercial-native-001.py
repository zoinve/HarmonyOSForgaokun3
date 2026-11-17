"""One authorized commercial boot with bounded observation and no retries."""
from pathlib import Path
import datetime,json,subprocess,time
root=Path(__file__).resolve().parents[1]/'reports/commercial61-native-001'
assert (root/'installation-result.json').is_file()
record=root/'boot-attempt.json';assert not record.exists()
before=subprocess.check_output(['ssh','matebook','cat /proc/sys/kernel/random/boot_id'],text=True,timeout=20).strip()
r=dict(start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),before_boot_id=before,
 entry='commercial61-native-001.conf',attempt_count=1,returned=False,sdk_userland=False)
record.open('x').write(json.dumps(r,indent=2))
startcode="import subprocess;subprocess.run(['bootctl','set-oneshot','commercial61-native-001.conf'],check=True);subprocess.run(['systemctl','reboot'],check=True)"
start=subprocess.run(['ssh','matebook','sudo -n python3 -'],input=startcode,text=True,capture_output=True,timeout=30)
r.update(reboot_command_exit=start.returncode,reboot_stdout=start.stdout,reboot_stderr=start.stderr)
if start.returncode!=0:
 (root/'boot-observation.json').open('x').write(json.dumps(r,indent=2));raise SystemExit('Reboot command failed; no retries')
query="""from pathlib import Path
import json,subprocess
print(json.dumps(dict(release=subprocess.check_output(['uname','-r'],text=True).strip(),boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),status=subprocess.check_output(['bootctl','status','--no-pager'],text=True),screenoff_timer=subprocess.run(['systemctl','is-enabled','harmony-lab-screen-off-001.timer'],text=True,capture_output=True).stdout.strip())))
"""
deadline=time.monotonic()+660
while time.monotonic()<deadline:
 time.sleep(20)
 try:
  q=subprocess.run(['ssh','-o','ConnectTimeout=5','matebook','sudo -n python3 -'],input=query,text=True,capture_output=True,timeout=15)
  if q.returncode:continue
  state=json.loads(q.stdout)
  if state['boot_id']==before:continue
  assert state['release']=='7.1.0-rc3-gaokun3+',state
  assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in state['status']
  assert 'OneShot Entry:' not in state['status'] and state['screenoff_timer']=='disabled'
  r.update(returned=True,ubuntu=state,return_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());break
 except subprocess.TimeoutExpired:pass
(root/'boot-observation.json').open('x').write(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if not r['returned']:raise SystemExit('No Ubuntu return observed within 11 minutes; do not retry boot')
