"""Exclusive FD characterization package; only the private probe changes."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
PARENT = runpy.run_path(str(BASE / 'build-composer-parser-001.py'), run_name='offline_builder')


def qemu_command(kernel, initrd):
    cmd = PARENT['qemu_command'](kernel, initrd)
    cmd[cmd.index('-accel') + 1] = 'tcg,thread=multi'
    cmd[cmd.index('-cpu') + 1] = 'cortex-a72'
    cmd[cmd.index('-append') + 1] = cmd[cmd.index('-append') + 1].replace('harmony.smq.parser=1', 'harmony.smq.fd=1')
    return cmd


def main():
    source = (BASE / 'build-composer-parser-001.py').read_text()
    for old, new in [('composer-parser-package-001', 'composer-fd-package-001'),
                     ('composer-parser-probe-001.cpp', 'composer-fd-probe-001.cpp')]:
        assert old in source
        source = source.replace(old, new)
    marker = '    OUT.mkdir()'
    assert source.count(marker) == 1
    source = source.replace(marker, "    assert hashlib.sha256(before['system/lib64/lab-softpipe-167/libhdifd_parcelable.z.so'][1]).hexdigest() == '9b7635a5e1ada2ad682c4c36cc7c07b631938673714fbfa03256c0fdae09fae8'\n" + marker)
    scope = dict(__name__='fd_package_builder', __file__=str(BASE / 'build-composer-parser-001.py'))
    exec(compile(source, 'fd-package-builder', 'exec'), scope)
    scope['main']()


if __name__ == '__main__':
    main()
