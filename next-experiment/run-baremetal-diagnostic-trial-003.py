"""Reuse immediate reconnect orchestration for one independent 006 observation trial."""
from pathlib import Path
import ast


def launcher_source():
    source = Path(__file__).with_name('run-baremetal-diagnostic-trial-002.py').read_text()
    for old, new in (
        ('native-trial-002', 'native-trial-003'),
        ('boot-entry-install-002', 'boot-entry-install-003'),
        ('baremetal-boot-entry-installed-002.json', 'baremetal-boot-entry-installed-003.json'),
        ('harmony-native-diag-005', 'harmony-native-diag-006'),
        ('trial-002-remote', 'trial-003-remote'),
        ('collector-trial-002', 'collector-trial-003'),
    ):
        assert old in source, old
        source = source.replace(old, new)
    # Keep the tested reconnect-002 implementation and immutable collector-001.
    ast.parse(source)
    return source


if __name__ == '__main__':
    exec(compile(launcher_source(), __file__, 'exec'), {'__file__': __file__, '__name__': '__main__'})
