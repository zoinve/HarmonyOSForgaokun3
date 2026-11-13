"""Launch scaled viewer on the existing MateBook graphical session."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/system-870'
subprocess.run(['scp', str(base / 'scaled-viewer.py'), 'matebook:' + remote + '/scaled-viewer.py'], check=True)
script = '''
import os,subprocess
from pathlib import Path
o=Path(REMOTE)
env=os.environ.copy()
settings=subprocess.check_output(['systemctl','--user','show-environment'],text=True)
env.update(dict(x.split('=',1) for x in settings.splitlines() if '=' in x))
with (o/'scaled-viewer.log').open('ab') as log:
 p=subprocess.Popen(['python3',str(o/'scaled-viewer.py'),str(o/'vnc.sock')],env=env,stdout=log,stderr=log,start_new_session=True)
print('Scaled viewer PID:',p.pid)
'''.replace('REMOTE', repr(remote))
r = subprocess.run(['ssh', 'matebook', 'python3 -'], input=script, text=True, capture_output=True, check=True)
print(r.stdout)
