"""Fresh TCG trial:001 is preserved as a failed pre-guest KVM attempt."""
from pathlib import Path


def launcher_source():
    source = (Path(__file__).with_name('run-composer-parser-001.py')).read_text()
    for old, new in [('reports/composer-parser-run-001', 'reports/composer-parser-run-002'),
                     ('composer-parser-runtime-001', 'composer-parser-runtime-002'),
                     ('composer-parser-runner-001', 'composer-parser-runner-002')]:
        assert old in source, old
        source = source.replace(old, new)
    old = "    command = builder.qemu_command(kernel, REMOTE + '/initramfs.cpio.gz')"
    assert source.count(old) == 1
    return source.replace(old, old + "\n    command[command.index('-accel') + 1] = 'tcg,thread=multi'\n    command[command.index('-cpu') + 1] = 'cortex-a72'")


if __name__ == '__main__':
    source = launcher_source()
    exec(compile(source, __file__ + ':generated', 'exec'))
