"""Exclusive original-SMQ prerequisite package; no device/service factory."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
PARENT = runpy.run_path(str(BASE / 'build-composer-fd-001.py'), run_name='offline_builder')


def qemu_command(kernel, initrd):
    cmd = PARENT['qemu_command'](kernel, initrd)
    i = cmd.index('-append') + 1
    cmd[i] = cmd[i].replace('harmony.smq.fd=1', 'harmony.smq.queue=1')
    return cmd


def main():
    source = (BASE / 'build-composer-fd-001.py').read_text()
    for old, new in [('composer-fd-package-001', 'composer-queue-package-001'),
                     ('composer-fd-probe-001.cpp', 'composer-queue-probe-001.cpp')]:
        assert old in source
        source = source.replace(old, new)
    scope = dict(__name__='queue_builder', __file__=str(BASE / 'build-composer-fd-001.py'))
    exec(compile(source, 'queue-builder', 'exec'), scope)
    scope['main']()


if __name__ == '__main__':
    main()
