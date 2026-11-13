"""Exclusive diskless parser package. Safe to import; no ELF is executed here."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

BASE = Path(__file__).resolve().parent
OUT = BASE.parent / 'reports/composer-parser-package-001'
PARENT_HASH = '3f654e55f9736d1138b5a444233916774acffd2fab99ec7dbb88bd65b82e9d8f'
SERVICE_HASH = 'c5f7b2430aac4bee8edbeaea707805c0d9f33f6ee762a4a1f82452be01f92aab'


def qemu_command(kernel, initrd):
    return ['qemu-system-aarch64', '-machine', 'virt,gic-version=3', '-cpu', 'host',
            '-accel', 'kvm', '-smp', '2', '-m', '512', '-nodefaults',
            '-kernel', str(kernel), '-initrd', str(initrd), '-append',
            'console=ttyAMA0 rdinit=/init panic=-1 loglevel=7 harmony.smq.parser=1',
            '-display', 'none', '-nic', 'none', '-serial', 'stdio',
            '-monitor', 'none', '-no-reboot']


def unpack(body):
    entries, pos = {}, 0
    raw = gzip.decompress(body)
    while True:
        head = raw[pos:pos + 110]
        assert head[:6] == b'070701'
        size, ns = int(head[54:62], 16), int(head[94:102], 16)
        name = raw[pos + 110:pos + 109 + ns].decode()
        start = (pos + 110 + ns + 3) & ~3
        pos = (start + size + 3) & ~3
        if name == 'TRAILER!!!':
            return entries
        assert name not in entries
        entries[name] = int(head[14:22], 16), raw[start:start + size]


def entry(name, mode, data, inode):
    nb = name.encode() + b'\0'
    values = [inode, mode, 0, 0, 1, 0, len(data), 0, 0, 0, 0, len(nb), 0]
    head = b'070701' + b''.join(f'{v:08x}'.encode() for v in values) + nb
    return head + b'\0' * (-len(head) % 4) + data + b'\0' * (-len(data) % 4)


def main():
    assert not OUT.exists(), OUT
    parent = (BASE / 'official-composer-service-957/initramfs.cpio.gz').read_bytes()
    assert hashlib.sha256(parent).hexdigest() == PARENT_HASH
    before = unpack(parent)
    service = 'system/lib64/lab-softpipe-167/libdisplay_composer_service_1.5.z.so'
    assert hashlib.sha256(before[service][1]).hexdigest() == SERVICE_HASH
    OUT.mkdir()
    linux = '/mnt/d/lab/HarmonyOSForMatebookego/'
    wrapper = '/home/zoinve/harmony-virgl-883/window-bridge/toolchain/ohos-platform-cxx'
    cmd = ['wsl', '-d', 'Debian', '--', wrapper, '-O2', '-std=c++17', '-Wall',
           '-Wextra', '-Werror', '-Wno-unused-command-line-argument',
           linux + 'next-experiment/composer-parser-probe-001.cpp', '-ldl',
           '-Wl,-rpath,/system/lib64/lab-softpipe-167',
           '-o', linux + 'reports/composer-parser-package-001/probe']
    p = subprocess.run(cmd, capture_output=True, timeout=120)
    for name, body in [('compile.stdout', p.stdout), ('compile.stderr', p.stderr)]:
        with (OUT / name).open('xb') as f:
            f.write(body)
    assert p.returncode == 0, p.stderr.decode(errors='replace')
    probe = (OUT / 'probe').read_bytes()
    assert probe[:6] == b'\x7fELF\x02\x01' and probe[18:20] == b'\xb7\0'
    after = dict(before)
    after['gpu-userspace-probe'] = 0o100755, probe
    archive = gzip.compress(b''.join(entry(n, m, b, i) for i, (n, (m, b))
                            in enumerate(sorted(after.items()), 1)) +
                            entry('TRAILER!!!', 0, b'', len(after) + 1), mtime=0)
    check = unpack(archive)
    assert set(check) == set(before)
    assert [n for n in before if before[n] != check[n]] == ['gpu-userspace-probe']
    with (OUT / 'initramfs.cpio.gz').open('xb') as f:
        f.write(archive)
    result = dict(parent_sha256=PARENT_HASH, service_sha256=SERVICE_HASH,
                  initrd_sha256=hashlib.sha256(archive).hexdigest(),
                  probe_sha256=hashlib.sha256(probe).hexdigest(),
                  original_records_unchanged=len(before) - 1,
                  only_probe_changed=True, elf_executed=False,
                  disks_attached=0, gpu_attached=False, desktop_verified=False)
    with (OUT / 'manifest.json').open('x') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
