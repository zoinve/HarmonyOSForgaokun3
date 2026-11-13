"""Diskless original SDK7 service loader and platform-container ABI test."""
from pathlib import Path
import gzip
import hashlib
import json
import posixpath
import re
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out, work = base / 'official-composer-service-957', root / 'composer-service-957-build2'
assert not out.exists() and not work.exists()
parent = base / 'official-composer-kms-952/initramfs.cpio.gz'
assert hashlib.sha256(parent.read_bytes()).hexdigest() == 'f90789f2f168ac24893a44ae3a9bef9ee9df8535f107234ee3280b464bb523c0'
entries, pos = {}, 0
raw = gzip.decompress(parent.read_bytes())
while True:
    h = raw[pos:pos+110]
    assert h[:6] == b'070701'
    size, ns = int(h[54:62], 16), int(h[94:102], 16)
    name = raw[pos+110:pos+109+ns].decode()
    start = (pos+110+ns+3)&~3
    pos = (start+size+3)&~3
    if name == 'TRAILER!!!': break
    assert name not in entries
    entries[name] = int(h[14:22],16), raw[start:start+size]
work.mkdir()
private = 'system/lib64/lab-softpipe-167/'
queue = ['libdisplay_composer_service_1.5.z.so']
seen, added = set(), []
folders = ['/lib64', '/lib64/chipset-sdk-sp', '/lib64/platformsdk', '/lib64/chipset-pub-sdk', '/lib64/chipset-sdk', '/lib64/ndk']
while queue:
    name = queue.pop()
    if name in seen or name == 'libc.so': continue  # Inherited official musl loader supplies libc.
    seen.add(name)
    if private+name in entries: continue
    found = None
    for partition in ('vendor', 'system'):
        image = '/mnt/d/Download/pc_all_arm/'+partition+'.img'
        for folder in folders:
            candidate = ('/system' if partition == 'system' else '')+folder+'/'+name
            for _ in range(12):
                stat = subprocess.run(['debugfs','-R','stat '+candidate,image],capture_output=True,text=True,check=True).stdout
                link = re.search(r'Fast link dest: "(.*?)"',stat)
                if not link: break
                candidate = posixpath.normpath(posixpath.join(posixpath.dirname(candidate),link[1]))
            if 'Type: regular' in stat:
                found = image, candidate
                break
        if found: break
    assert found, ('missing dependency',name)
    dest = work/name
    subprocess.run(['debugfs','-R',f'dump {found[1]} {dest}',found[0]],capture_output=True,check=True)
    body = dest.read_bytes();assert body.startswith(b'\x7fELF')
    entries[private+name] = 0o100444,body
    if name == 'libdisplay_composer_service_1.5.z.so':
        entries['vendor/lib64/'+name] = 0o100444,body
    queue.extend(re.findall(r'\(NEEDED\).*?\[(.*?)\]',subprocess.check_output(['readelf','-dW',str(dest)],text=True)))
    added.append(dict(name=name,source=found,sha256=hashlib.sha256(body).hexdigest()))
ref = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports')
source = (ref/'tests/composer-service-probe.cpp').read_text().replace('/vendor/lib64/aurora-graphics/','/vendor/lib64/').replace('service_1.3','service_1.5')
symbols = subprocess.check_output(['aarch64-linux-gnu-nm','-D',str(work/'libdisplay_composer_service_1.5.z.so')],text=True)
for symbol in re.findall(r'"(_ZN[^"\n]+)"',source):
    assert re.search(r'\b'+re.escape(symbol)+r'$',symbols,re.M),symbol
source = source.replace('    setbuf(stdout, nullptr);','    setbuf(stdout, nullptr); alarm(40);\n    static_assert(sizeof(Capability)==80 && sizeof(Property)==40 && sizeof(Mode)==16);')
source = '#include <unistd.h>\n'+source
(work/'probe.cpp').write_text(source)
subprocess.run([str(root/'window-bridge/toolchain/ohos-platform-cxx'),'-O2','-std=c++17','-Wall','-Wextra','-I'+str(ref/'graphics/include'),str(work/'probe.cpp'),'-ldl','-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(work/'probe')],check=True)
entries['gpu-userspace-probe'] = 0o100755,(work/'probe').read_bytes()
def entry(name,mode,data,inode):
    nb=name.encode()+b'\0'
    values=[inode,mode,0,0,1,0,len(data),0,0,0,0,len(nb),0]
    head=b'070701'+b''.join(f'{v:08x}'.encode() for v in values)+nb
    return head+b'\0'*(-len(head)%4)+data+b'\0'*(-len(data)%4)
archive=gzip.compress(b''.join(entry(n,m,b,i) for i,(n,(m,b)) in enumerate(sorted(entries.items()),1))+entry('TRAILER!!!',0,b'',len(entries)+1),mtime=0)
out.mkdir();(out/'initramfs.cpio.gz').write_bytes(archive)
(out/'manifest.json').write_text(json.dumps(dict(initrd_sha256=hashlib.sha256(archive).hexdigest(),parent_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),added_original_dependencies=added,disks_attached=0,desktop_verified=False),indent=2))
print((out/'manifest.json').read_text())
