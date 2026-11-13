"""Install candidate 005 independently; preserve consumed 004 and all old EFI files."""
from pathlib import Path
import ast


def launcher_source():
    source = Path(__file__).with_name('install-baremetal-diagnostic-entry-001.py').read_text()
    changes = {
        'baremetal-boot-entry-preflight-001.json': 'baremetal-boot-entry-preflight-002.json',
        'baremetal-boot-entry-installed-001.json': 'baremetal-boot-entry-installed-002.json',
        'boot-entry-install-001': 'boot-entry-install-002',
        'harmony-native-diag-004': 'harmony-native-diag-005',
        'native-diagnostic-init-004/': 'native-diagnostic-init-005/',
        '884772104ac2f858697a1730d0f8307db05a9155c3b677355f881c1939b120e1':
            'f3e990cb4215c551f086a851ba767cd7411e686a909203fd9a20ae09a2de5a16',
        'native hardware diagnostic 004': 'native hardware diagnostic 005',
    }
    for old, new in changes.items():
        assert old in source, old
        source = source.replace(old, new)
    ast.parse(source)
    return source


if __name__ == '__main__':
    exec(compile(launcher_source(), __file__, 'exec'), {'__file__': __file__, '__name__': '__main__'})
