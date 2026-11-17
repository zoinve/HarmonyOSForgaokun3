"""Exercise the actual HarmonyMac gate, not a substitute readiness algorithm."""
from pathlib import Path
import runpy, subprocess
base=Path(__file__).resolve().parent
assert (base/'commercial-reference-start-036.py').exists(), 'reference startup adapter missing'
m=runpy.run_path(str(base/'commercial-reference-start-036.py'))
script=m['desktop_start']()
reference=m['REFERENCE'].joinpath('ports/tests/native-desktop-start.sh').read_text()
gate=reference[reference.index('n=0\n'):reference.index('/system/bin/aa start')]
assert gate.strip() in script
assert 'force-stop' not in script and 'NATIVE_DESKTOP_READY' not in script
assert 'param set' not in script and 'hidumper' not in script
remote='script='+repr(script)+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
for ready_after,expected in [(2,0),(999,1)]:
 with tempfile.TemporaryDirectory(prefix='reference-start036-') as directory:
  root=Path(directory);count=root/'count';count.write_text('0');launch=root/'launch'
  def exe(name,text):
   p=root/name;p.write_text('#!/bin/sh\n'+text);p.chmod(0o755);return str(p)
  probe=exe('probe',f'n=$(cat {count}); n=$((n+1)); echo "$n" > {count}\n[ "$n" -ge {ready_after} ]\n')
  aa=exe('aa',f'printf "%s\\n" "$*" > {launch}\n')
  sleep=exe('sleep','exit 0\n')
  actual=script.replace('/system/bin/aurora/samgr-service-probe',probe).replace('/usr/bin/aa',aa).replace('sleep 1',sleep)
  p=subprocess.run(['sh','-c',actual],capture_output=True,text=True,timeout=10)
  assert p.returncode==expected,(p.returncode,p.stderr)
  assert int(count.read_text())==(3 if expected==0 else 121)
  assert launch.exists()==(expected==0)
  if launch.exists():assert launch.read_text().strip()=='start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard'
print('PASS: reference service gate delays original launch and fails closed on timeout')
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=remote,text=True,check=True,timeout=30)
