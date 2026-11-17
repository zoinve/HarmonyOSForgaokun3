"""Read device metadata and evdev axis limits, never input event contents."""
from pathlib import Path
import datetime
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
PAYLOAD = r'''
from pathlib import Path
import errno,fcntl,json,os,stat,struct,sys
def read(path):
 try:
  with Path(path).open('rb') as stream:data=stream.read(65537)
  if len(data)>65536:return dict(error='size_limit')
  return data.decode('utf-8').strip()
 except (OSError,UnicodeError) as exc:return dict(error=type(exc).__name__,errno=getattr(exc,'errno',None))
def link(path):
 try:return Path(path).resolve(strict=True).name
 except OSError:return None
def attrs(path,names):return {name:read(path/name) for name in names if (path/name).exists()}
def permissions(path):
 try:
  s=path.stat()
  return dict(uid=s.st_uid,gid=s.st_gid,mode=oct(stat.S_IMODE(s.st_mode)))
 except OSError as exc:return dict(errno=exc.errno)
def axes(path):
 result={}
 try:fd=os.open(path,os.O_RDONLY|os.O_NONBLOCK|os.O_CLOEXEC)
 except OSError as exc:return dict(open_errno=exc.errno)
 try:
  supported=int.from_bytes(fcntl.ioctl(fd,0x80084523,bytes(8)),sys.byteorder)
  # EVIOCGABS only queries current axis metadata; never consume input events.
  for code in [0,1,24,47,48,49,53,54,57,58]:
   if not supported & (1<<code):continue
   try:
    values=struct.unpack('6i',fcntl.ioctl(fd,0x80184540+code,bytes(24)))
    result[str(code)]=dict(zip(['minimum','maximum','fuzz','flat','resolution'],values[1:]))
   except OSError as exc:
    if exc.errno!=errno.EINVAL:result[str(code)]=dict(errno=exc.errno)
 except OSError as exc:result['capabilities_errno']=exc.errno
 finally:os.close(fd)
 return result
result=dict(context='Ubuntu metadata only; not HarmonyOS physical interaction acceptance',kernel=os.uname().release,
 boot_id=read('/proc/sys/kernel/random/boot_id'),read_only=True,input_events_read=False,usb_mode_changed=False)
result['input']=[]
for p in sorted(Path('/sys/class/input').glob('event*')):
 device=p/'device'
 result['input'].append(dict(node=p.name,**attrs(device,['name','id/bustype','id/vendor','id/product','properties','capabilities/ev','capabilities/key','capabilities/abs','capabilities/rel']),
  permissions=permissions(Path('/dev/input')/p.name),axes=axes(Path('/dev/input')/p.name)))
result['usb']=[]
for p in sorted(Path('/sys/bus/usb/devices').glob('*')):
 if not ((p/'idVendor').exists() or (p/'bInterfaceClass').exists()):continue
 result['usb'].append(dict(node=p.name,driver=link(p/'driver'),**attrs(p,['idVendor','idProduct','bDeviceClass','bInterfaceClass','bInterfaceSubClass','bInterfaceProtocol','product','speed','authorized','busnum','devnum'])))
result['usb_device_nodes']=[dict(node=str(p),**permissions(p)) for p in sorted(Path('/dev/bus/usb').glob('*/*'))]
result['usb_roles']=[dict(node=p.name,role=read(p/'role')) for p in sorted(Path('/sys/class/usb_role').glob('*'))]
result['typec']=[dict(node=p.name,**attrs(p,['data_role','power_role','port_type'])) for p in sorted(Path('/sys/class/typec').glob('port*')) if '-partner' not in p.name]
result['platform_bindings']=[dict(node=p.name,driver=link(p/'driver'),modalias=read(p/'modalias')) for p in sorted(Path('/sys/bus/platform/devices').glob('*')) if any(s in p.name for s in ['.usb','xhci','88ea000','88e5000','8902000'])]
result['modules']=[line.split()[0] for line in read('/proc/modules').splitlines()]
result['usb_storage']=[dict(node=p.name,**attrs(p,['removable','ro','size']),driver=link(p/'device/driver')) for p in sorted(Path('/sys/class/block').glob('*')) if '/usb' in str(p.resolve())]
print(json.dumps(result))
'''


if __name__ == '__main__':
    runpy.run_path(str(BASE / 'commercial-workflow-145.py'))['configure_local_transport']()
    proc = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
        '-o', 'ConnectTimeout=8', '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
        'matebook', 'sudo -n python3 -'], input=PAYLOAD, text=True, capture_output=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    report = BASE.parent / 'reports' / ('input-usb-147-' + stamp)
    report.mkdir()
    (report / 'result.json').open('x').write(json.dumps(data, indent=2))
    print(json.dumps(dict(report=str(report.relative_to(BASE.parent)), input=data['input'], usb=data['usb'],
        usb_roles=data['usb_roles'], typec=data['typec'], usb_storage=data['usb_storage']), indent=2))
