"""Fresh full-system copies: change only our EGL bridge, retain official policy."""
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
trial = json.loads((base / 'official-display-capability-943/result.json').read_text())
assert all(trial[k] for k in ('child_exit_zero', 'default_selected', 'native_present_pass'))
work = Path('/home/zoinve/harmony-virgl-883/official-system-944')
out = base / 'official-system-944'
assert not work.exists() and not out.exists(), 'Never overwrite numbered experiments'
old = json.loads((base / 'official-system-941/manifest.json').read_text())


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


for row in old['images']:
    assert sha(row['path']) == row['sha256']
for row in old['original_inputs']:
    assert sha(Path('/mnt/d/Download/pc_all_arm') / row['name']) == row['sha256']
archive = base / 'official-display-capability-943/initramfs.cpio.gz'
assert sha(archive) == '1fcb2dd4be736dd1401218efcea7d900c6dc416c208076ecbbdc10edd394b8b0'
raw = gzip.decompress(archive.read_bytes())
pos = 0
bridge = None
while True:
    h = raw[pos:pos + 110]
    assert h[:6] == b'070701'
    size, n = int(h[54:62], 16), int(h[94:102], 16)
    name = raw[pos + 110:pos + 109 + n].decode()
    start = (pos + 110 + n + 3) & ~3
    pos = (start + size + 3) & ~3
    if name == 'system/lib64/lab-softpipe-167/libEGL_impl.so':
        assert bridge is None
        bridge = raw[start:start + size]
    if name == 'TRAILER!!!':
        break
assert bridge is not None and hashlib.sha256(bridge).hexdigest() == '20426afb3254aced34486dc5d13fc7502d74a256f5c63f39ad9e607fe247af4d'
work.mkdir()
out.mkdir()
images = []
for row, name in zip(old['images'], ('system', 'vendor')):
    dest = work / (name + '-graphics.img')
    shutil.copyfile(row['path'], dest)
    images.append(dest)
system = images[0]
payload = work / 'bridge.so'
payload.write_bytes(bridge)
label = work / 'system-lib.label'
label.write_bytes(b'u:object_r:system_lib_file:s0\0')
path = '/system/lib64/lab-softpipe-167/libEGL_impl.so'
operations = ['rm ' + path, f'write {payload} {path}',
              f'set_inode_field {path} mode 0100644',
              f'ea_set -f {label} {path} security.selinux']
for command in operations:
    assert system.parent == work and system.name == 'system-graphics.img'
    subprocess.run(['debugfs', '-w', '-R', command, str(system)], check=True, capture_output=True)
check = work / 'bridge-verified.so'
subprocess.run(['debugfs', '-R', f'dump {path} {check}', str(system)], check=True, capture_output=True)
assert check.read_bytes() == bridge
for image in images:
    r = subprocess.run(['e2fsck', '-fn', str(image)], capture_output=True, text=True)
    (out / (image.name + '.fsck.txt')).write_text(r.stdout + r.stderr)
    assert r.returncode == 0, (image, r.returncode)
assert sha(images[1]) == old['images'][1]['sha256']
for row in old['images']:
    assert sha(row['path']) == row['sha256']
for row in old['original_inputs']:
    assert sha(Path('/mnt/d/Download/pc_all_arm') / row['name']) == row['sha256']
result = dict(images=[dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p)) for p in images],
              parent_images=old['images'], original_inputs=old['original_inputs'],
              changed_file=path, bridge_sha256=sha(check), operations=operations,
              original_images_unchanged=True, selinux_policy_modified=False,
              init_modified=False, activation_modified=False, desktop_verified=False)
(out / 'manifest.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
