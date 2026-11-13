"""Exclusive private FD-word/vector package; no device or service factory."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
PARENT = runpy.run_path(str(BASE / 'build-composer-fd-001.py'), run_name='offline_builder')


def qemu_command(kernel, initrd):
    cmd = PARENT['qemu_command'](kernel, initrd)
    i = cmd.index('-append') + 1
    cmd[i] = cmd[i].replace('harmony.smq.fd=1', 'harmony.smq.fdstream=1')
    return cmd


def main():
    source = (BASE / 'build-composer-fd-001.py').read_text()
    for old, new in [('composer-fd-package-001', 'composer-fdstream-package-001'),
                     ('composer-fd-probe-001.cpp', 'composer-fdstream-probe-001.cpp')]:
        assert old in source
        source = source.replace(old, new)
    scope = dict(__name__='fdstream_builder', __file__=str(BASE / 'build-composer-fd-001.py'))
    exec(compile(source, 'fdstream-builder', 'exec'), scope)
    scope['main']()


if __name__ == '__main__':
    main()
