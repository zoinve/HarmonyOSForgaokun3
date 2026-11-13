"""Package UCSI-only 007 independently; never install an entry or reboot."""
from pathlib import Path
import ast
import runpy


def launcher_source():
    base = Path(__file__).resolve().parent
    source = (base / 'prepare-baremetal-diagnostic-init-004.py').read_text()
    anchor = "'deadline-004')"
    assert source.count(anchor) == 1
    source = source.replace(anchor, "'deadline-004', 'display-005', 'observation-006', 'ucsi-007')")
    for old, new in (
        ('baremetal-diagnostic-init-004', 'baremetal-diagnostic-init-007'),
        ('native-diagnostic-init-004', 'native-diagnostic-init-007'),
        ('diagnostic-004-generated', 'diagnostic-007-generated'),
    ):
        source = source.replace(old, new)
    namespace = {'__file__': str(base / 'prepare-baremetal-diagnostic-init-007.py'), '__name__': 'offline_generator'}
    exec(compile(source, '007-adapter', 'exec'), namespace)
    result = namespace['launcher_source']()
    ast.parse(result)
    return result


if __name__ == '__main__':
    exec(compile(launcher_source(), 'diagnostic-007-generated', 'exec'))
