"""Offline, separately named graphics adaptation copies; never edit SDK originals.

Run under WSL Debian. All debugfs write commands target new copies only.
"""
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import subprocess

local = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
work = Path('/home/zoinve/harmony-virgl-883/official-system-941')
out = local / 'official-system-941'
assert not work.exists() and not out.exists(), 'Completed numbered experiments are immutable'
source = Path('/mnt/d/Download/pc_all_arm')
archive = local / 'official-native-gbm-940/initramfs.cpio.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest() == '78226918d24c526971b9793755dac6e44bdda1eb79f8448d547d6f55ad056067'
inputs = json.loads((local.parent / 'reports/official-arm-sdk-921-inputs.json').read_text())['files']

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

for row in inputs:
    assert sha(source / row['name']) == row['sha256']
work.mkdir()
out.mkdir()
staging = work / 'files'
staging.mkdir()
raw = gzip.decompress(archive.read_bytes())
entries = {}
pos = 0
while True:
    h = raw[pos:pos + 110]
    assert h[:6] == b'070701'
    size, n = int(h[54:62], 16), int(h[94:102], 16)
    name = raw[pos + 110:pos + 109 + n].decode()
    data = (pos + 110 + n + 3) & ~3
    pos = (data + size + 3) & ~3
    if name == 'TRAILER!!!':
        break
    assert name not in entries
    entries[name] = (int(h[14:22], 16), raw[data:data + size])

private = '/system/lib64/lab-softpipe-167'
regulars = {'libEGL.so.1.0.0', 'libGLESv1_CM.so.1.1.0', 'libGLESv2.so.2.0.0',
            'libEGL_impl.so', 'libgbm.so.1.0.0', 'libdrm.so.2.124.0',
            'libexpat.so.1.10.2', 'libgallium-25.0.1.so', 'libc++_shared.so'}
links = {'libEGL.so.1': 'libEGL.so.1.0.0', 'libGLESv1_CM.so.1': 'libGLESv1_CM.so.1.1.0',
         'libGLESv2.so.2': 'libGLESv2.so.2.0.0', 'libgbm.so.1': 'libgbm.so.1.0.0',
         'libdrm.so.2': 'libdrm.so.2.124.0', 'libexpat.so.1': 'libexpat.so.1.10.2'}
ops = []

def debug(image, command, write=False):
    assert image.parent == work and image.name in ('system-graphics.img', 'vendor-graphics.img')
    cmd = ['debugfs'] + (['-w'] if write else []) + ['-R', command, str(image)]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if write:
        ops.append(dict(image=image.name, command=command))
    return r.stdout, r.stderr

system = work / 'system-graphics.img'
vendor = work / 'vendor-graphics.img'
shutil.copyfile(source / 'system.img', system)
shutil.copyfile(source / 'vendor.img', vendor)
for path in (private, '/system/lib64/lab-virgl883'):
    stdout, stderr = debug(system, 'stat ' + path)
    assert 'File not found' in stderr, (path, stdout, stderr)

labels = {}
for label in ('system_lib_file', 'vendor_lib_file'):
    p = staging / (label + '.label')
    p.write_bytes(('u:object_r:' + label + ':s0').encode() + b'\0')
    labels[label] = p

def label(image, path, kind):
    debug(image, f'ea_set -f {labels[kind]} {path} security.selinux', True)

def add_file(image, dest, body, kind):
    p = staging / (hashlib.sha256(dest.encode()).hexdigest() + '.so')
    p.write_bytes(body)
    debug(image, f'write {p} {dest}', True)
    debug(image, f'set_inode_field {dest} mode 0100644', True)
    label(image, dest, kind)
    probe = staging / (p.name + '.verify')
    debug(image, f'dump {dest} {probe}')
    assert probe.read_bytes() == body, dest

debug(system, 'mkdir ' + private, True)
label(system, private, 'system_lib_file')
for name in sorted(regulars):
    mode, body = entries[private.lstrip('/') + '/' + name]
    assert mode & 0o170000 == 0o100000 and body[:4] == b'\x7fELF', name
    add_file(system, private + '/' + name, body, 'system_lib_file')
for name, target in links.items():
    debug(system, f'symlink {private}/{name} {target}', True)
    label(system, private + '/' + name, 'system_lib_file')
# Mesa's compiled-in GBM search directory uses this alias; no environment edits.
debug(system, f'symlink /system/lib64/lab-virgl883 lab-softpipe-167', True)
label(system, '/system/lib64/lab-virgl883', 'system_lib_file')
debug(system, 'mkdir ' + private + '/gbm', True)
label(system, private + '/gbm', 'system_lib_file')
for name, (mode, body) in entries.items():
    prefix = private.lstrip('/') + '/gbm/'
    if not name.startswith(prefix):
        continue
    relative = name[len(prefix):]
    assert '/' not in relative
    if mode & 0o170000 == 0o120000:
        debug(system, f'symlink {private}/gbm/{relative} {body.decode()}', True)
        label(system, private + '/gbm/' + relative, 'system_lib_file')
    else:
        add_file(system, private + '/gbm/' + relative, body, 'system_lib_file')

for name in ('libEGL_impl.so', 'libGLESv1_impl.so', 'libGLESv2_impl.so', 'libGLESv3_impl.so'):
    path = '/system/lib64/' + name
    stdout, _ = debug(system, 'stat ' + path)
    assert 'Type: symlink' in stdout and 'libdgles.z.so' in stdout
    backup = path + '.sdk-original'
    debug(system, f'symlink {backup} libdgles.z.so', True)
    label(system, backup, 'system_lib_file')
    debug(system, 'rm ' + path, True)
    target = 'libEGL_impl.so' if name == 'libEGL_impl.so' else ('libGLESv1_CM.so.1' if name == 'libGLESv1_impl.so' else 'libGLESv2.so.2')
    debug(system, f'symlink {path} lab-softpipe-167/{target}', True)
    label(system, path, 'system_lib_file')

# Preserve the official vendor VDI contents beside the adapted entry in this copy.
vpath = '/lib64/libdisplay_buffer_vdi_impl.z.so'
saved = staging / 'official-vdi.so'
debug(vendor, f'dump {vpath} {saved}')
assert saved.stat().st_size == 9160
add_file(vendor, vpath + '.sdk-original', saved.read_bytes(), 'vendor_lib_file')
debug(vendor, 'rm ' + vpath, True)
add_file(vendor, vpath, entries['vendor/lib64/libdisplay_buffer_vdi_impl.z.so'][1], 'vendor_lib_file')

for row in inputs:
    assert sha(source / row['name']) == row['sha256'], row['name']
result = dict(original_images_unchanged=True, selinux_policy_modified=False,
              init_modified=False, activation_modified=False, desktop_verified=False,
              images=[dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p)) for p in (system, vendor)],
              operations=ops, original_inputs=inputs)
(out / 'manifest.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
