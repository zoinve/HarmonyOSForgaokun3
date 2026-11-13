"""Install independent observation-only 006; preserve prior consumed entries."""
from pathlib import Path
import ast


def launcher_source():
    source = Path(__file__).with_name('install-baremetal-diagnostic-entry-001.py').read_text()
    changes = {
        'baremetal-boot-entry-preflight-001.json': 'baremetal-boot-entry-preflight-003.json',
        'baremetal-boot-entry-installed-001.json': 'baremetal-boot-entry-installed-003.json',
        'boot-entry-install-001': 'boot-entry-install-003',
        'harmony-native-diag-004': 'harmony-native-diag-006',
        'native-diagnostic-init-004/': 'native-diagnostic-init-006/',
        '884772104ac2f858697a1730d0f8307db05a9155c3b677355f881c1939b120e1':
            '842e29b1c4a78fbbed4d2784f7833e7fffaca483eeedcc2cdc649fe576d4276e',
        'native hardware diagnostic 004': 'native hardware diagnostic 006',
    }
    for old, new in changes.items():
        assert old in source, old
        source = source.replace(old, new)
    ast.parse(source)
    return source


if __name__ == '__main__':
    exec(compile(launcher_source(), __file__, 'exec'), {'__file__': __file__, '__name__': '__main__'})
