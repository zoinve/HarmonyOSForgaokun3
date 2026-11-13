"""Single authorized unattended boot; bounded SSH observation, never auto retry boot."""
from pathlib import Path
import subprocess,json,time,datetime
root=Path(__file__).resolve().parent.parent/'reports/native-original-graphics-boot-033'
record=root/'boot-attempt.json'
assert not record.exists()
before=subprocess.check_output(['ssh','matebook','cat /proc/sys/kernel/random/boot_id'],text=True,timeout=20).strip()
r=dict(start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),before_boot_id=before,
 entry='native-original-graphics-033.conf',attempt_count=1,returned=False)
with record.open('x') as f:json.dump(r,f,indent=2)
cmd="sudo -n bootctl set-oneshot native-original-graphics-033.conf && sudo -n systemctl reboot"
start=subprocess.run(['ssh','matebook',cmd],text=True,capture_output=True,timeout=30)
r['reboot_command_exit']=start.returncode;r['reboot_stdout']=start.stdout;r['reboot_stderr']=start.stderr
if start.returncode!=0:
 (root/'boot-observation.json').write_text(json.dumps(r,indent=2));raise SystemExit('Reboot command failed; no retries')
deadline=time.monotonic()+660
while time.monotonic()<deadline:
 time.sleep(20)
 try:
  q=subprocess.run(['ssh','-o','ConnectTimeout=5','matebook','uname -r; cat /proc/sys/kernel/random/boot_id; sudo -n bootctl status --no-pager; systemctl is-active harmony-lab-screen-off-001.timer'],text=True,capture_output=True,timeout=15)
  lines=q.stdout.splitlines()
  if q.returncode==0 and len(lines)>1 and lines[1]!=before:
   assert lines[0]=='7.1.0-rc3-gaokun3+',q.stdout
   assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in q.stdout
   assert 'OneShot Entry:' not in q.stdout
   r.update(returned=True,after_boot_id=lines[1],ubuntu_status=q.stdout,
      return_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
   break
 except subprocess.TimeoutExpired:pass
with (root/'boot-observation.json').open('x') as f:json.dump(r,f,indent=2)
print(json.dumps(r,indent=2))
if not r['returned']:raise SystemExit('No Ubuntu return observed within 11 minutes; do not reboot again')
