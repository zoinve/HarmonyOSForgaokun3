"""Read selected public hardware attributes; never export serials or credentials."""
from pathlib import Path
import datetime
import json
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
PAYLOAD=r'''
from pathlib import Path
import json,os
def read(path):
 try:return Path(path).read_text().strip()[:4096]
 except (OSError,UnicodeError):return None
def attrs(root,fields):return {field:read(root/field) for field in fields if (root/field).exists()}
def linkname(path):
 try:return path.resolve(strict=True).name
 except OSError:return None
result=dict(kernel=os.uname().release,boot_id=read('/proc/sys/kernel/random/boot_id'),
    system_context='harmony' if Path('/system/bin/sa_main').exists() else 'linux_host',
    collected_read_only=True,serials_and_addresses_excluded=True)
result['input']=[dict(node=p.name,driver=linkname(p/'device/driver'),**attrs(p/'device',['name','id/bustype','id/vendor','id/product','capabilities/ev','capabilities/key','capabilities/abs','capabilities/rel'])) for p in sorted(Path('/sys/class/input').glob('event*'))]
result['network']=[dict(node=p.name,driver=linkname(p/'device/driver'),**attrs(p,['operstate','carrier','type'])) for p in sorted(Path('/sys/class/net').glob('*'))]
result['drm']=[dict(node=p.name,**attrs(p,['status','enabled','modes'])) for p in sorted(Path('/sys/class/drm').glob('card*-*'))]
result['power_supply']=[dict(node=p.name,driver=linkname(p/'device/driver'),**attrs(p,['type','present','online','status','capacity','voltage_now','current_now','temp','charge_full','charge_now','energy_full','energy_now'])) for p in sorted(Path('/sys/class/power_supply').glob('*'))]
result['backlight']=[dict(node=p.name,**attrs(p,['brightness','actual_brightness','max_brightness','bl_power','type'])) for p in sorted(Path('/sys/class/backlight').glob('*'))]
result['sound_cards']=read('/proc/asound/cards')
result['sound_pcm']=read('/proc/asound/pcm')
result['sound_nodes']=[p.name for p in sorted(Path('/dev/snd').glob('*'))]
result['bluetooth']=[dict(node=p.name,driver=linkname(p/'device/driver')) for p in sorted(Path('/sys/class/bluetooth').glob('hci*'))]
result['usb']=[dict(node=p.name,driver=linkname(p/'driver'),**attrs(p,['idVendor','idProduct','bDeviceClass','bInterfaceClass','product'])) for p in sorted(Path('/sys/bus/usb/devices').glob('*')) if (p/'idVendor').exists() or (p/'bInterfaceClass').exists()]
result['modules']=[line.split()[0] for line in (read('/proc/modules') or '').splitlines()]
print(json.dumps(result))
'''

if __name__=='__main__':
    runpy.run_path(str(BASE/'commercial-workflow-124.py'))['configure_local_transport']()
    result=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','-o','HostName=192.168.10.128','-o','HostKeyAlias=192.168.10.128','matebook','sudo -n python3 -'],input=PAYLOAD,text=True,capture_output=True,timeout=45)
    assert result.returncode==0,result.stderr
    data=json.loads(result.stdout)
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder=BASE.parent/'reports'/('basic-driver-baseline-001-'+stamp)
    folder.mkdir()
    (folder/'result.json').open('x').write(json.dumps(data,indent=2))
    print(json.dumps(dict(report=str(folder/'result.json'),**data),indent=2))
