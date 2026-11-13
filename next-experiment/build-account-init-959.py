"""Append a diagnostic PID1 wrapper; preserve every original initramfs byte."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
out=base/'official-account-init-959'
assert not out.exists()
parent=base/'official-arm-mount-921/initramfs.cpio.gz'
manifest=json.loads((parent.parent/'manifest.json').read_text())
assert hashlib.sha256(parent.read_bytes()).hexdigest()==manifest['initramfs_sha256']
raw=gzip.decompress(parent.read_bytes());pos=0
while True:
    start=pos;h=raw[pos:pos+110];assert h[:6]==b'070701'
    size,ns=int(h[54:62],16),int(h[94:102],16)
    name=raw[pos+110:pos+109+ns].decode();data=(pos+110+ns+3)&~3
    pos=(data+size+3)&~3
    if name=='TRAILER!!!':break
    assert name!='lab-account-init'
out.mkdir()
subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(base/'account-init-959.c'),'-o',str(out/'lab-account-init')],check=True)
def entry(name,body,mode,ino):
    n=name.encode()+b'\0';v=[ino,mode,0,0,1,0,len(body),0,0,0,0,len(n),0]
    block=b'070701'+b''.join(f'{x:08x}'.encode() for x in v)+n
    block+=b'\0'*(-len(block)%4);block+=body
    return block+b'\0'*(-len(block)%4)
body=raw[:start]+entry('lab-account-init',(out/'lab-account-init').read_bytes(),0o100755,990001)+entry('TRAILER!!!',b'',0,990002)
assert body[:start]==raw[:start]
archive=gzip.compress(body,mtime=0);(out/'initramfs.cpio.gz').write_bytes(archive)
result=dict(sha256=hashlib.sha256(archive).hexdigest(),original_archive_prefix_unchanged=True,original_init_unchanged=True,account_operation='official acm create normal labuser; no password or switch',desktop_verified=False)
(out/'manifest.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
