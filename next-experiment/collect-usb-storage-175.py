"""Collect only USB/storage metadata; never mount, open a raw disk or read serials."""
from pathlib import Path
import json
import runpy
import subprocess
import sys

BASE = Path(__file__).resolve().parent
REPORT = BASE.parent / 'reports/commercial61-native-175-compile-fix-1'
PAYLOAD = r'''
from pathlib import Path
import datetime,json,re,subprocess
def read(path):
    try:return Path(path).read_text().strip()
    except (OSError,UnicodeError):return None
devices=[]
for path in sorted(Path('/sys/class/block').iterdir()):
    resolved=path.resolve()
    ancestor=None
    for parent in [resolved,*resolved.parents]:
        if (parent/'subsystem').resolve()==Path('/sys/bus/usb') and (parent/'idVendor').is_file():
            ancestor=parent;break
    if ancestor is None:continue
    devices.append(dict(name=path.name,vid=read(ancestor/'idVendor'),pid=read(ancestor/'idProduct'),
        attributes={key:read(path/key) for key in ['dev','size','ro','removable','partition']}))
tree=json.loads(subprocess.check_output(['lsblk','--json','--bytes','-o','NAME,TYPE,SIZE,TRAN,FSTYPE,MOUNTPOINTS'],text=True))
def filtered(node):
    return dict(name=node['name'],type=node['type'],bytes=node['size'],filesystem=node.get('fstype'),
        mounted=any(node.get('mountpoints') or []),children=[filtered(child) for child in node.get('children',[])])
usb=[filtered(node) for node in tree['blockdevices'] if node.get('tran')=='usb']
usb_ids=[]
for line in subprocess.check_output(['lsusb'],text=True).splitlines():
    match=re.match(r'Bus (\d+) Device (\d+): ID ([0-9a-f]{4}):([0-9a-f]{4})',line)
    if match:usb_ids.append(dict(bus=int(match[1]),address=int(match[2]),vid=match[3],pid=match[4]))
print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    ubuntu_boot_id=read('/proc/sys/kernel/random/boot_id'),usb=usb_ids,usb_block_sysfs=devices,
    usb_block_filesystems=usb,raw_blocks_opened=False,media_written=False,serials_read=False)))
'''


if __name__ == '__main__':
    assert sys.argv[1:] in [['preboot'], ['preboot-ready'], ['postboot']]
    phase = sys.argv[1]
    output = REPORT / ('usb-' + phase + '.json')
    assert not output.exists(), 'preserve previous collection'
    runpy.run_path(str(BASE / 'commercial-workflow-175.py'))['configure_local_transport']()
    proc = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
        '-o', 'ConnectTimeout=8', '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
        'matebook', 'python3 -'], input=PAYLOAD, text=True, capture_output=True, timeout=45)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    expected = [row for row in data['usb_block_sysfs'] if row['vid']=='346d' and row['pid']=='5678' and
                row['attributes']['removable']=='1' and row['attributes']['partition'] is None and
                row['attributes']['size']=='61849600']
    data['expected_unique_disk_present'] = len(expected) == 1
    def mounted(node):
        return node['mounted'] or any(mounted(child) for child in node['children'])
    data['all_usb_volumes_unmounted'] = not any(mounted(node) for node in data['usb_block_filesystems'])
    output.open('x').write(json.dumps(data, indent=2))
    print(json.dumps(data, indent=2))
    assert data['expected_unique_disk_present'], 'expected disk not present; do not boot or retry automatically'
    if phase == 'preboot-ready':
        assert len(data['usb_block_filesystems']) == 1 and data['all_usb_volumes_unmounted'], 'USB media still mounted or extra disk present'
