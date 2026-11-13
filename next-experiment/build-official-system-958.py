"""Change only the composer VDI in a fresh copy of adapted vendor949."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'official-system-958';out=base/'official-system-958'
assert not work.exists() and not out.exists()
assert json.loads((base/'official-composer-service-957/result.json').read_text())['probe_pass']
assert json.loads((base/'official-composer-rfb-956/result.json').read_text())['rfb_pattern_verified']
old=json.loads((base/'official-system-949/manifest.json').read_text())
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def originals():
    for row in old['original_inputs']:
        assert sha(Path('/mnt/d/Download/pc_all_arm')/row['name'])==row['sha256']
originals()
for row in old['images']:assert sha(row['path'])==row['sha256']
body=(root/'composer-kms-952-build2/libdisplay_composer_vdi_impl.z.so').read_bytes()
work.mkdir();out.mkdir()
vendor=work/'vendor-graphics.img'
shutil.copyfile(old['images'][1]['path'],vendor)
payload=work/'composer.so';payload.write_bytes(body)
label=work/'vendor-lib.label';label.write_bytes(b'u:object_r:vendor_lib_file:s0\0')
path='/lib64/libdisplay_composer_vdi_impl.z.so'
operations=[]
def debug(command,write=False):
    assert vendor.parent==work and vendor.name=='vendor-graphics.img'
    r=subprocess.run(['debugfs']+(['-w'] if write else [])+['-R',command,str(vendor)],capture_output=True,text=True,check=True)
    assert 'Filesystem not open' not in r.stderr,r.stderr
    if write:operations.append(command)
    return r
backup=work/'sdk-original.so'
debug(f'dump {path} {backup}')
assert backup.read_bytes()==(root/'composer-inspect-951/libdisplay_composer_vdi_impl.z.so').read_bytes()
for dest,p in [(path+'.sdk-original',backup),(path,payload)]:
    if dest==path:debug('rm '+path,True)
    debug(f'write {p} {dest}',True)
    debug(f'set_inode_field {dest} mode 0100644',True)
    debug(f'ea_set -f {label} {dest} security.selinux',True)
    check=work/(p.name+'.verified');debug(f'dump {dest} {check}')
    assert check.read_bytes()==p.read_bytes()
r=subprocess.run(['e2fsck','-fn',str(vendor)],capture_output=True,text=True)
(out/'vendor-fsck.txt').write_text(r.stdout+r.stderr);assert r.returncode==0
originals()
for row in old['images']:assert sha(row['path'])==row['sha256']
result=dict(images=[old['images'][0],dict(path=str(vendor),bytes=vendor.stat().st_size,sha256=sha(vendor))],original_inputs=old['original_inputs'],parent_images=old['images'],composer_sha256=hashlib.sha256(body).hexdigest(),changed_file=path,operations=operations,original_images_unchanged=True,init_modified=False,activation_modified=False,selinux_policy_modified=False,desktop_verified=False)
(out/'manifest.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
