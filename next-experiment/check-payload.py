"""Validate headless payload selection before any remote lifecycle action."""
from pathlib import Path
import hashlib
import sys

path=Path(__file__).with_name('run.py').resolve()
payload=path.parent/'payload-873'/'initramfs.cpio.gz'
number=next(n for n in range(9873,100000) if not (path.parent/f'run-{n}').exists())
sys.argv=[str(path),str(number),'--quiet-trace','--relative-mouse','--initramfs',str(payload)]
text=path.read_text()
ns={'__file__':str(path)}
exec(compile(text[:text.index("subprocess.run(['ssh', 'matebook', 'mkdir '")],str(path),'exec'),ns)
c=ns['c']
assert c['command'][c['command'].index('-initrd')+1]==ns['remote']+'/initramfs.cpio.gz'
assert c['inputs'][1]['sha256']==hashlib.sha256(payload.read_bytes()).hexdigest()
assert 'physical_screen_viewer_pid' not in ns['source']
assert c['command'][c['command'].index('-display')+1]=='none'
assert c['command'][c['command'].index('-accel')+1]=='kvm'
assert 'usb-mouse' in c['command']
print('PASS: fresh hash-pinned initramfs, native KVM and no physical viewer')
