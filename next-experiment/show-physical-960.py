"""Show the existing VM on the authorized physical display; never restart QEMU."""
from pathlib import Path
import subprocess

viewer=(Path(__file__).resolve().parent/'scaled-viewer.py').read_text()
viewer=viewer.replace("connection = socket.socket(socket.AF_UNIX)\nconnection.connect(endpoint)",
                      "connection = socket.socket(fileno=int(os.environ['HARMONY_VIEWER_FD']))")
remote=r'''
import os,pwd,socket,subprocess,json
from pathlib import Path
viewer_source=__VIEWER_SOURCE__
endpoint=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/full-system-960/vnc.sock')
assert endpoint.is_socket(), 'Current VM is no longer running; do not relaunch completed experiments'
user=pwd.getpwnam('gdm-greeter');runtime=Path('/run/user')/str(user.pw_uid)
assert (runtime/'wayland-0').is_socket()
conn=socket.socket(socket.AF_UNIX);conn.connect(str(endpoint))
env=os.environ.copy()
env.update(HOME=user.pw_dir,USER=user.pw_name,LOGNAME=user.pw_name,
 XDG_RUNTIME_DIR=str(runtime),WAYLAND_DISPLAY='wayland-0',GDK_BACKEND='wayland',
 DBUS_SESSION_BUS_ADDRESS='unix:path='+str(runtime/'bus'),HARMONY_VIEWER_FD=str(conn.fileno()))
drop=f'import os;os.setgroups([]);os.setgid({user.pw_gid});os.setuid({user.pw_uid});'
# The privileged launcher opens only the VM socket; the UI runs as the greeter user.
payload=drop+f'import sys;sys.argv=["harmony-vm-viewer",{str(endpoint)!r}];exec(compile({viewer_source!r},"harmony-vm-viewer","exec"))'
log=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/full-system-960/physical-viewer.log')
assert not log.exists(), 'Do not duplicate the viewer'
with log.open('xb') as output:
 p=subprocess.Popen(['/usr/bin/python3','-u','-c',payload],env=env,pass_fds=(conn.fileno(),),stdout=output,stderr=output,start_new_session=True)
conn.close()
for backlight in Path('/sys/class/backlight').glob('*'):
 maximum=int((backlight/'max_brightness').read_text());current=int((backlight/'brightness').read_text())
 if current==0:(backlight/'brightness').write_text(str(maximum//2))
 print('BACKLIGHT',backlight.name,(backlight/'brightness').read_text().strip())
command=['/usr/bin/gdbus','call','--session','--dest','org.gnome.Mutter.DisplayConfig','--object-path','/org/gnome/Mutter/DisplayConfig','--method','org.freedesktop.DBus.Properties.Set','org.gnome.Mutter.DisplayConfig','PowerSaveMode','<int32 0>']
r=subprocess.run(['/usr/sbin/runuser','-u',user.pw_name,'--']+command,env=env,capture_output=True,text=True,timeout=10)
print(json.dumps(dict(viewer_pid=p.pid,display_wake_returncode=r.returncode,display_wake_output=r.stdout+r.stderr)))
'''.replace('__VIEWER_SOURCE__',repr(viewer))
r=subprocess.run(['ssh','matebook','sudo -n python3 -'],input=remote,text=True,capture_output=True)
print(r.stdout,r.stderr)
r.check_returncode()
