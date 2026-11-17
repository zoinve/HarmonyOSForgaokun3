"""Locate the original wired-detection contract and real jack event devices."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/audio-jack-contract-375'
REPOSITORY = 'openharmony/multimedia_audio_framework'
BRANCH = 'OpenHarmony-6.0-Release'
PREFIX = 'services/audio_policy/server/domain/device/'
FILES = [
    'src/pnp/audio_input_thread.cpp', 'src/pnp/audio_input_thread.h',
    'src/pnp/audio_pnp_server.cpp', 'src/pnp/audio_pnp_param.h',
    'src/pnp/audio_socket_thread.cpp', 'src/device_status_listener.cpp',
]
REMOTE = r'''
from pathlib import Path
import array,fcntl,json,os
assert Path('/proc/asound/card0/id').read_text().strip()=='SC8280XPHUAWEIG'
assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='GK-W7X'
rows=[]
def query(fd,number,length):
    data=bytearray(length)
    fcntl.ioctl(fd,(2<<30)|(length<<16)|(ord('E')<<8)|number,data,True)
    return data
def bit(data,n):return bool(data[n//8]&(1<<(n%8)))
for event in sorted(Path('/sys/class/input').glob('event*'),key=lambda p:int(p.name[5:])):
    row=dict(event=event.name,name=(event/'device/name').read_text().strip())
    fd=None
    try:
        fd=os.open('/dev/input/'+event.name,os.O_RDONLY|os.O_CLOEXEC|os.O_NONBLOCK|os.O_NOFOLLOW)
        types=query(fd,0x20,8)
        row['ev_sw']=bit(types,5)
        if row['ev_sw']:
            caps=query(fd,0x25,8);state=query(fd,0x1b,8)
            row['switches']=[i for i in range(17) if bit(caps,i)]
            row['active_switches']=[i for i in row['switches'] if bit(state,i)]
            row['headphone_capable']=bit(caps,2)
            row['microphone_capable']=bit(caps,4)
    except OSError as e:row['error']=e.errno
    finally:
        if fd is not None:os.close(fd)
    rows.append(row)
print(json.dumps(dict(input_devices=rows,read_only=True,events_consumed=False,
    controls_modified=False,microphone_recorded=False),indent=2))
'''
IMAGE_CHECK = r'''
import json,re,runpy
read=runpy.run_path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/build-radio-native-261.py')['image_read']
data=read('p111-system.kr990-ext4-v1.img','/system/lib64/libaudio_policy_service.z.so')
strings=set(re.findall(rb'[ -~]{8,}',data))
need=[b'AudioPnpInputOpen',b'AudioPnpUeventOpen',b'AudioAnalogHeadsetDeviceCheck',
      b'/sys/class/switch/h2w/state',b'AudioPnpInputPollAndRead']
paths=[b'/dev/input/event'+str(i).encode() for i in range(1,5)]
assert all(s in strings for s in need+paths)
print(json.dumps(dict(original_library='/system/lib64/libaudio_policy_service.z.so',
    bytes=len(data),detector_symbols=[s.decode() for s in need],
    hardcoded_event_paths=[s.decode() for s in paths],source_image_modified=False)))
'''

if __name__ == '__main__':
    assert not REPORT.exists()
    with urllib.request.urlopen('https://gitee.com/api/v5/repos/'+REPOSITORY+
            '/commits/'+BRANCH,timeout=30) as response:
        revision=json.load(response)['sha']
    sources=[]
    for path in FILES:
        url='https://gitee.com/'+REPOSITORY+'/raw/'+revision+'/'+PREFIX+path
        with urllib.request.urlopen(url,timeout=30) as response:data=response.read()
        assert b'Copyright' in data and not data.startswith(b'<!DOCTYPE')
        sources.append((path,data,dict(path=PREFIX+path,url=url,bytes=len(data),
            sha256=hashlib.sha256(data).hexdigest())))
    ssh=runpy.run_path(str(ROOT/'next-experiment/deploy-settings-data-198.py'))['SSH']
    remote=subprocess.run(ssh+['sudo -n python3 -'],input=REMOTE,text=True,
        capture_output=True,check=True,timeout=45)
    inventory=json.loads(remote.stdout)
    image=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=IMAGE_CHECK,
        text=True,capture_output=True,check=True,timeout=45)
    result=dict(source_repository=REPOSITORY,revision=revision,branch=BRANCH,
        sources=[row for _,_,row in sources],hardware_inventory=inventory,
        image_contract=json.loads(image.stdout),headphone_hotplug_verified=False)
    REPORT.mkdir()
    for path,data,_ in sources:(REPORT/Path(path).name).open('xb').write(data)
    (REPORT/'result.json').open('x').write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
