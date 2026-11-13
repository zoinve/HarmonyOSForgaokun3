"""Reopen only the viewer for experiment 870; never stops or restarts QEMU."""
import subprocess

script = r'''
import os, signal, subprocess, socket, json
from pathlib import Path
o=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/system-870')
env=os.environ.copy()
settings=subprocess.check_output(['systemctl','--user','show-environment'],text=True)
env.update(dict(l.split('=',1) for l in settings.splitlines() if '=' in l))
assert env.get('DISPLAY') and env.get('XAUTHORITY')
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  if (proc/'comm').read_text().strip()!='vncviewer':continue
  args=(proc/'cmdline').read_bytes().split(b'\0')
  if str(o/'vnc.sock').encode() in args:os.kill(int(proc.name),signal.SIGTERM)
 except (FileNotFoundError,ProcessLookupError,PermissionError):pass
with (o/'viewer-fullscreen.log').open('ab') as log:
 p=subprocess.Popen(['vncviewer','-Shared','-FullScreen','-AlwaysCursor','-CursorType=System','-RemoteResize=0','-ViewOnly=0',str(o/'vnc.sock')],env=env,stdout=log,stderr=log,start_new_session=True)
print('Full-screen viewer PID:',p.pid)
'''
r = subprocess.run(['ssh', 'matebook', 'python3 -'], input=script, text=True, capture_output=True, check=True)
print(r.stdout)
