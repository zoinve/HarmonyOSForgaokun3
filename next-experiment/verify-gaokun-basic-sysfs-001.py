"""Cross-build and read real sysfs on the target; never set brightness here."""
from pathlib import Path
import base64
import datetime
import hashlib
import json
import runpy
import subprocess
import tempfile

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    runpy.run_path(str(BASE/'commercial-workflow-124.py'))['configure_local_transport']()
    with tempfile.TemporaryDirectory(prefix='gaokun-live-sysfs-build-') as directory:
        binary=Path(directory)/'backend.so'
        subprocess.run(['aarch64-linux-gnu-gcc','-std=c11','-Wall','-Wextra','-Werror','-fPIC','-shared',str(BASE/'gaokun-basic-sysfs-001.c'),'-o',str(binary)],check=True)
        data=binary.read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    code='binary='+repr(base64.b64encode(data).decode())+'\nexpected='+repr(digest)+'\n'+r'''
from pathlib import Path
import base64,ctypes,hashlib,json,os,tempfile
class Battery(ctypes.Structure):
 _fields_=[('valid',ctypes.c_uint32),('present',ctypes.c_int),('capacity',ctypes.c_int),('status',ctypes.c_int),('voltage',ctypes.c_int64),('current',ctypes.c_int64),('temperature',ctypes.c_int64)]
folder=Path(tempfile.mkdtemp(prefix='gaokun-sysfs-readonly-'))
path=folder/'backend.so'
try:
 data=base64.b64decode(binary);assert hashlib.sha256(data).hexdigest()==expected
 with path.open('xb') as stream:stream.write(data)
 path.chmod(0o600)
 library=ctypes.CDLL(str(path))
 library.gaokun_battery_read.argtypes=[ctypes.c_char_p,ctypes.POINTER(Battery)]
 library.gaokun_backlight_get.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_uint32)]
 battery=Battery();level=ctypes.c_uint32()
 battery_rc=library.gaokun_battery_read(b'/sys/class/power_supply/gaokun-ec-battery',ctypes.byref(battery))
 brightness_rc=library.gaokun_backlight_get(b'/sys/class/backlight/ae96000.dsi.0',ctypes.byref(level))
 assert battery_rc==0 and brightness_rc==0,(battery_rc,brightness_rc)
 assert battery.valid&15==15
 result=dict(system_context='harmony' if Path('/system/bin/sa_main').exists() else 'linux_host',kernel=os.uname().release,
  backend_sha256=expected,battery_return=battery_rc,brightness_return=brightness_rc,
  battery={name:getattr(battery,name) for name,_ in Battery._fields_},brightness_255=level.value,
  device_read_only=True,brightness_set_called=False,harmony_service_integration_verified=False)
finally:
 path.unlink(missing_ok=True);folder.rmdir()
print(json.dumps(result))
'''
    remote=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','-o','HostName=192.168.10.128','-o','HostKeyAlias=192.168.10.128','matebook','python3 -'],input=code,text=True,capture_output=True,timeout=45)
    assert remote.returncode==0,remote.stderr
    result=json.loads(remote.stdout)
    result['source_sha256']={name:hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in ['gaokun-basic-sysfs-001.c','gaokun-basic-sysfs-001.h']}
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder=BASE.parent/'reports'/('gaokun-basic-sysfs-live-001-'+stamp)
    folder.mkdir()
    (folder/'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(dict(report=str(folder/'result.json'),**result),indent=2))
