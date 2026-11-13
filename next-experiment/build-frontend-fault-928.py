"""Fresh diskless fault observation; no changes to official ELF libraries."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
out = base / 'official-frontend-probe-928'
work = Path('/home/zoinve/harmony-virgl-883/frontend-fault-928')
assert not out.exists() and not work.exists()
work.mkdir()
cc = '/home/zoinve/harmony-virgl-883/window-bridge/toolchain/ohos-cc'
subprocess.run([cc, '-shared', '-fPIC', '-O1', '-Wall', '-Wextra',
                str(base / 'frontend-fault-928.c'), '-o', str(work / 'fault.so')], check=True)
source = (base / 'gpu-userspace-init.c').read_text()
anchor = '        setenv("EGL_LOG_LEVEL", "debug", 1);'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n        setenv("LD_PRELOAD", "/frontend-fault.so", 1);')
(work / 'init.c').write_text(source)
subprocess.run(['aarch64-linux-gnu-gcc', '-static', '-O2', str(work / 'init.c'),
                '-o', str(work / 'init')], check=True)
original = base / 'official-frontend-probe-927/initramfs.cpio.gz'
assert hashlib.sha256(original.read_bytes()).hexdigest() == 'bc74b70fa721ad97c37838e09a605790eeccdca092616cb1ac0c21d7f457f215'
raw = gzip.decompress(original.read_bytes())
pos = 0
chunks = []
def entry(name, body, mode, inode):
    nb = name.encode() + b'\0'
    values = [inode, mode, 0, 0, 1, 0, len(body), 0, 0, 0, 0, len(nb), 0]
    h = b'070701' + b''.join(f'{v:08x}'.encode() for v in values) + nb
    return h + b'\0' * (-len(h) % 4) + body + b'\0' * (-len(body) % 4)
while True:
    start = pos
    h = raw[pos:pos+110]
    assert h[:6] == b'070701'
    size, ns = int(h[54:62], 16), int(h[94:102], 16)
    name = raw[pos+110:pos+109+ns].decode()
    data = (pos+110+ns+3) & ~3
    pos = (data+size+3) & ~3
    if name == 'TRAILER!!!':
        break
    chunks.append(entry('init', (work/'init').read_bytes(), 0o100755, 990001)
                  if name == 'init' else raw[start:pos])
chunks.append(entry('frontend-fault.so', (work/'fault.so').read_bytes(), 0o100444, 990002))
chunks.append(entry('TRAILER!!!', b'', 0, 990003))
archive = gzip.compress(b''.join(chunks), mtime=0)
out.mkdir()
(out/'initramfs.cpio.gz').write_bytes(archive)
(out/'manifest.json').write_text(json.dumps(dict(initrd_sha256=hashlib.sha256(archive).hexdigest(),
    source_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
    changed_entries=['init'], added_entries=['frontend-fault.so'],
    official_libraries_unchanged=True, disks_attached=0, desktop_verified=False), indent=2))
print((out/'manifest.json').read_text())
