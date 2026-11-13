"""One candidate007 UCSI trial with the existing immediate SSH observer/collector."""
from pathlib import Path
import ast


def launcher_source():
    source = Path(__file__).with_name('run-baremetal-diagnostic-trial-002.py').read_text()
    for old, new in (
        ('native-trial-002', 'native-trial-004'),
        ('boot-entry-install-002', 'boot-entry-install-004'),
        ('baremetal-boot-entry-installed-002.json', 'baremetal-boot-entry-installed-004.json'),
        ('harmony-native-diag-005', 'harmony-native-diag-007'),
        ('trial-002-remote', 'trial-004-remote'),
        ('collector-trial-002', 'collector-trial-004'),
    ):
        assert old in source, old
        source = source.replace(old, new)
    ast.parse(source)
    return source


if __name__ == '__main__':
    exec(compile(launcher_source(), __file__, 'exec'), {'__file__': __file__, '__name__': '__main__'})
