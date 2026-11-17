"""Execute the bounded launcher against a late BMS fixture, including false CLI success."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'commercial-desktop-retry-032.py').is_file(),'missing bounded desktop launch retry'
repair=runpy.run_path(str(base/'commercial-desktop-retry-032.py'))['repair']
old=(base.parent/'reports/commercial61-native-031/matebook-account-order.sh').read_text()
new=repair(old)
anchor='# Reference: HarmonyMac ports/tests/native-desktop-start.sh, normal Ability Manager entry.'
assert new.split(anchor)[0]==old.split(anchor)[0]
assert new.count('/usr/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard')==1
for forbidden in ['param set','force-stop','setuid','sandbox-switch',' -u 100']:
    assert forbidden not in new
try:repair(new)
except AssertionError:pass
else:raise AssertionError('reapplied repair accepted')
code='tail='+repr(new[new.index(anchor):])+'\n'+r'''
from pathlib import Path
import os,subprocess,tempfile
for ready_after,already,expected_calls,expected_exit in [(2,False,2,0),(999,False,6,1),(1,True,0,0)]:
 with tempfile.TemporaryDirectory(prefix='desktop-retry032-') as d:
  root=Path(d);count=root/'count';flag=root/'process';count.write_text('0')
  if already:flag.touch()
  def executable(name,text):
   p=root/name;p.write_text('#!/bin/sh\n'+text);p.chmod(0o755);return str(p)
  pidof=executable('pidof','test -e '+str(flag)+'\n')
  aa=executable('aa',f'n=$(cat {count}); n=$((n+1)); echo "$n" > {count}\nif [ "$n" -ge {ready_after} ]; then touch {flag}; fi\necho "request diagnostic only"\nexit 0\n')
  sleep=executable('sleep','exit 0\n')
  source=tail.replace('/system/bin/pidof',pidof).replace('/usr/bin/aa',aa).replace('/system/bin/sleep',sleep).replace('/dev/kmsg',str(root/'kmsg'))
  source='#!/bin/sh\nset -u\nread_param(){ printf true; }\n'+source
  result=subprocess.run(['sh','-c',source],capture_output=True,text=True,timeout=5)
  assert result.returncode==expected_exit,(result.returncode,result.stderr)
  assert int(count.read_text())==expected_calls,(ready_after,count.read_text())
print('PASS: real shell retries late readiness, ignores false CLI success, stops on process and remains bounded')
'''
r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=code,text=True,capture_output=True,timeout=30)
print(r.stdout);assert r.returncode==0,r.stderr
