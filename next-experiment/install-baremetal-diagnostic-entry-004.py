"""Install UCSI-only candidate007 independently, retaining all prior entries."""
from pathlib import Path
import ast


def launcher_source():
    source = Path(__file__).with_name('install-baremetal-diagnostic-entry-001.py').read_text()
    changes = {
        'baremetal-boot-entry-preflight-001.json': 'baremetal-boot-entry-preflight-004.json',
        'baremetal-boot-entry-installed-001.json': 'baremetal-boot-entry-installed-004.json',
        'boot-entry-install-001': 'boot-entry-install-004',
        'harmony-native-diag-004': 'harmony-native-diag-007',
        'native-diagnostic-init-004/': 'native-diagnostic-init-007/',
        '884772104ac2f858697a1730d0f8307db05a9155c3b677355f881c1939b120e1':
            'd0a16f3db2fcc42837783ca704fa6cfd448b301a84c1bdb96fc24f0b4e887bb2',
        'native hardware diagnostic 004': 'native hardware diagnostic 007',
    }
    for old, new in changes.items():
        assert old in source, old
        source = source.replace(old, new)
    ast.parse(source)
    return source


if __name__ == '__main__':
    exec(compile(launcher_source(), __file__, 'exec'), {'__file__': __file__, '__name__': '__main__'})
