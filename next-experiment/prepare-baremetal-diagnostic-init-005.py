"""Generate fresh offline 005 archive; never install or reboot."""
from pathlib import Path
import ast
import runpy


def launcher_source():
    base = Path(__file__).resolve().parent
    source = (base / 'prepare-baremetal-diagnostic-init-004.py').read_text()
    source = source.replace("'deadline-004')", "'deadline-004', 'display-005')")
    source = source.replace('baremetal-diagnostic-init-004', 'baremetal-diagnostic-init-005')
    source = source.replace('native-diagnostic-init-004', 'native-diagnostic-init-005')
    source = source.replace('diagnostic-004-generated', 'diagnostic-005-generated')
    namespace = {'__file__': str(base / 'prepare-baremetal-diagnostic-init-005.py'), '__name__': 'offline_generator'}
    exec(compile(source, '005-adapter', 'exec'), namespace)
    result = namespace['launcher_source']()
    ast.parse(result)
    return result


if __name__ == '__main__':
    exec(compile(launcher_source(), 'diagnostic-005-generated', 'exec'))
