"""Throwaway diskless test of the working WSI with SDK 7 runtime libraries.

Run with WSL Debian Python. No SDK image is opened for writing.
"""
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import re
import posixpath

local = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = local / 'official-window-probe-925'
work = root / 'official-window-probe-925'
resume = sys.argv[1:] == ['--resume-incomplete']
assert not (out / 'initramfs.cpio.gz').exists()
if resume:
    assert out.is_dir() and work.is_dir()
else:
    assert not out.exists() and not work.exists()
    out.mkdir()
    work.mkdir()
ram = work / 'ramroot'
if not resume:
    shutil.copytree(root / 'frame-observer-913/ramroot', ram, symlinks=True)
image = '/mnt/d/Download/pc_all_arm/system.img'
runtime = {
    '/system/lib/ld-musl-aarch64.so.1': ram / 'lib/ld-musl-aarch64.so.1',
    '/system/lib64/chipset-sdk-sp/libc++.so': ram / 'gpu883-libs/libc++.so',
    '/system/lib64/chipset-sdk-sp/libbuffer_handle.z.so': ram / 'gpu883-libs/libbuffer_handle.z.so',
}
for original, dest in runtime.items():
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_symlink() or dest.exists():
        dest.unlink()  # Only this new, disposable RAM-root copy.
    subprocess.run(['debugfs', '-R', f'dump {original} {dest}', image], check=True)
    assert dest.is_file() and dest.read_bytes().startswith(b'\x7fELF'), original
    print('EXTRACTED', original, dest.stat().st_size)

# Resolve the original SDK's handle-library dependency closure, not stub DSOs.
private = ram / 'gpu883-libs'
queue = [private / 'libbuffer_handle.z.so', private / 'libc++.so']
seen = set()
while queue:
    current = queue.pop()
    if current.name in seen:
        continue
    seen.add(current.name)
    dynamic = subprocess.check_output(['readelf', '-dW', str(current)], text=True)
    for needed in re.findall(r'\(NEEDED\).*?\[(.*?)\]', dynamic):
        if needed == 'libc.so':
            continue
        if (private / needed).exists():
            queue.append(private / needed)
            continue
        for folder in ('/system/lib64', '/system/lib64/chipset-sdk-sp',
                       '/system/lib64/platformsdk', '/system/lib64/chipset-pub-sdk',
                       '/system/lib64/chipset-sdk', '/system/lib64/ndk'):
            candidate = folder + '/' + needed
            for _ in range(8):
                stat = subprocess.run(['debugfs', '-R', 'stat ' + candidate, image],
                                      text=True, capture_output=True).stdout
                link = re.search(r'Fast link dest: "(.*?)"', stat)
                if not link:
                    break
                candidate = posixpath.normpath(posixpath.join(posixpath.dirname(candidate), link[1]))
            if 'Type: regular' not in stat:
                continue
            dest = private / needed
            subprocess.run(['debugfs', '-R', f'dump {candidate} {dest}', image], check=True)
            assert dest.read_bytes().startswith(b'\x7fELF'), needed
            queue.append(dest)
            print('DEPENDENCY', needed, candidate)
            break
        else:
            raise AssertionError(('unresolved original SDK dependency', needed))
lib = ram / 'lib'
lib.mkdir(exist_ok=True)
if not (lib / 'libc.so').exists():
    (lib / 'libc.so').symlink_to('ld-musl-aarch64.so.1')
alias = ram / 'system/lib64/lab-virgl883'
alias.parent.mkdir(parents=True, exist_ok=True)
assert not alias.exists()
alias.symlink_to('lab-softpipe-167')
# The existing fixture checks real GPU pixels and queue semantics, not a desktop.
assert (ram / 'gpu883-libs/gpu912-window-probe').is_file()
shutil.copy2(ram / 'gpu883-libs/gpu912-window-probe', ram / 'gpu-userspace-probe')
# Full-system payloads retain their bind source at /gpu883-libs.
assert (ram / 'gpu-userspace-probe').is_file()
target = ram / 'system/lib64/lab-softpipe-167'
assert not target.exists()
shutil.copytree(ram / 'gpu883-libs', target, symlinks=True)
shutil.copy2(local / 'gpu-runtime-883/init', ram / 'init')

def entry(name, mode, body, inode):
    nb = name.encode() + b'\0'
    fields = [inode, mode, 0, 0, 1, 0, len(body), 0, 0, 0, 0, len(nb), 0]
    header = b'070701' + b''.join(f'{v:08x}'.encode() for v in fields)
    head = header + nb
    head += b'\0' * (-len(head) % 4)
    return head + body + b'\0' * (-len(body) % 4)

files, chunks = [], []
for inode, path in enumerate(sorted(ram.rglob('*')), 1):
    name = path.relative_to(ram).as_posix()
    if path.is_symlink():
        import os
        mode, body = 0o120777, os.readlink(path).encode()
    elif path.is_dir():
        mode, body = 0o40755, b''
    else:
        mode = 0o100755 if name in ('init', 'gpu-userspace-probe') else 0o100444
        body = path.read_bytes()
    chunks.append(entry(name, mode, body, inode))
    files.append(dict(path=name, mode=oct(mode), bytes=len(body), sha256=hashlib.sha256(body).hexdigest()))
chunks.append(entry('TRAILER!!!', 0, b'', len(files) + 1))
archive = gzip.compress(b''.join(chunks), mtime=0)
(out / 'initramfs.cpio.gz').write_bytes(archive)
manifest = dict(initrd_sha256=hashlib.sha256(archive).hexdigest(), files=files,
                disks_attached=0, desktop_verified=False,
                runtime_sources=list(runtime), original_sdk_modified=False)
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print('BUILT', manifest['initrd_sha256'], 'runtime test not yet executed')
