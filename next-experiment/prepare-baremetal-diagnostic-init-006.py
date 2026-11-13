"""Package independent observation-only 006; never install an entry or reboot."""
from pathlib import Path
import ast


def launcher_source():
    base = Path(__file__).resolve().parent
    source = (base / 'prepare-baremetal-diagnostic-init-004.py').read_text()
    anchor = "'deadline-004')"
    assert source.count(anchor) == 1
    source = source.replace(anchor, "'deadline-004', 'display-005', 'observation-006')")
    for old, new in (
        ('baremetal-diagnostic-init-004', 'baremetal-diagnostic-init-006'),
        ('native-diagnostic-init-004', 'native-diagnostic-init-006'),
        ('diagnostic-004-generated', 'diagnostic-006-generated'),
    ):
        source = source.replace(old, new)
    namespace = {'__file__': str(base / 'prepare-baremetal-diagnostic-init-006.py'), '__name__': 'offline_generator'}
    exec(compile(source, '006-adapter', 'exec'), namespace)
    result = namespace['launcher_source']()
    ast.parse(result)
    return result


if __name__ == '__main__':
    exec(compile(launcher_source(), 'diagnostic-006-generated', 'exec'))
