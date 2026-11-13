"""3120x2080 guest output, absolute USB pointer, aspect-preserving viewer."""
from pathlib import Path
base=Path(__file__).resolve().parent
source=(base/'run-official-display-961.py').read_text()
source=source.replace('full-system-961','full-system-962').replace('official-arm-run-961','official-arm-run-962')
source=source.replace('userdata-cleanup-official-960.json','userdata-cleanup-official-961.json')
anchor="vendor=c['disks'][1]['path']"
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'''
assert c['command'].count('virtio-gpu-gl-pci,xres=1920,yres=1080')==1
assert c['command'].count('usb-mouse')==1
c['command']=[a.replace('virtio-gpu-gl-pci,xres=1920,yres=1080', 'virtio-gpu-gl-pci,xres=3120,yres=2080') for a in c['command']]
c['command'][c['command'].index('usb-mouse')]='usb-tablet'
c['requested_guest_resolution']=[3120,2080]
c['requested_pointer_mode']='absolute USB tablet'
''')
exec(compile(source,'native-display-962-generated','exec'))
