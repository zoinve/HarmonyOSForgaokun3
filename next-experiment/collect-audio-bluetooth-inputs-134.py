"""Read actual board driver/module bindings without changing audio or Bluetooth."""
from pathlib import Path
import datetime
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
PAYLOAD = r'''
from pathlib import Path
import json,os,re
def read(path,limit=1048576):
 try:
  with Path(path).open('rb') as stream:data=stream.read(limit+1)
  assert len(data)<=limit,('refusing truncated attribute',str(path))
  return data.decode('utf-8').strip()
 except (OSError,UnicodeError):return None
def linkname(path):
 try:return path.resolve(strict=True).name
 except OSError:return None
def bindings(node):
 device=node/'device'
 try:real=device.resolve(strict=True)
 except OSError:return []
 result=[]
 for parent in [real,*real.parents]:
  if not (parent/'driver').exists():continue
  result.append(dict(device=parent.name,driver=linkname(parent/'driver'),module=linkname(parent/'driver/module')))
 return result
text=read('/proc/modules')
assert text is not None
modules=[]
for line in text.splitlines():
 fields=line.split()
 assert len(fields)>=6,fields[:3]
 modules.append(dict(name=fields[0],bytes=int(fields[1]),uses=int(fields[2]),used_by=[] if fields[3]=='-' else fields[3].strip(',').split(',')))
selected=[row for row in modules if re.match(r'^(snd|soundwire|q6|qcom_q6|bt|bluetooth|hci|qcom_glink|qcom_pdr|qrtr|rpmsg|qmi|apr|fastrpc)',row['name'])]
result=dict(kernel=os.uname().release,boot_id=read('/proc/sys/kernel/random/boot_id'),
 context='linux_host_not_harmony_hdi_acceptance',collected_read_only=True,
 hardware_serials_and_network_addresses_not_read=True,modules_complete_not_4096_byte_truncated=True,
 all_module_names=[row['name'] for row in modules],selected_modules=selected,
 cards=read('/proc/asound/cards'),pcm=read('/proc/asound/pcm'),
 sound_nodes=[p.name for p in sorted(Path('/dev/snd').glob('*'))],
 sound_bindings=[dict(node=p.name,id=read(p/'id'),bindings=bindings(p)) for p in sorted(Path('/sys/class/sound').glob('card[0-9]*'))],
 remoteproc=[dict(node=p.name,name=read(p/'name'),state=read(p/'state'),firmware=read(p/'firmware'),bindings=bindings(p)) for p in sorted(Path('/sys/class/remoteproc').glob('remoteproc*'))],
 bluetooth=[dict(node=p.name,bindings=bindings(p)) for p in sorted(Path('/sys/class/bluetooth').glob('hci*'))])
print(json.dumps(result))
'''


if __name__ == '__main__':
    runpy.run_path(str(BASE / 'commercial-workflow-124.py'))['configure_local_transport']()
    result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                             '-o', 'ConnectTimeout=8', '-o', 'HostName=192.168.10.128',
                             '-o', 'HostKeyAlias=192.168.10.128', 'matebook', 'sudo -n python3 -'],
                            input=PAYLOAD, text=True, capture_output=True, timeout=45)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    report = BASE.parent / 'reports' / ('audio-bluetooth-inputs-134-' + stamp)
    report.mkdir()
    (report / 'result.json').open('x').write(json.dumps(data, indent=2))
    print(json.dumps(dict(report=str(report / 'result.json'), **{key: value for key, value in data.items() if key != 'all_module_names'}), indent=2))
