"""Fresh offline 003 packaging; inherit the exact verified 002 packaging gates."""
from pathlib import Path
import ast
import runpy


def launcher_source():
    base = Path(__file__).resolve().parent
    source = (base / 'prepare-baremetal-diagnostic-init-002.py').read_text()
    source = source.replace("candidate = generate((base / 'baremetal-diagnostic-init.c').read_text())",
        "candidate = generate((base / 'baremetal-diagnostic-init.c').read_text())\n"
        "    candidate = runpy.run_path(str(base / 'baremetal-diagnostic-board-003.py'))['build_source'](candidate)")
    # Only fresh output names change. Keep the parent's 001 builder as the
    # implementation source and 002 storage generator as the input source.
    source = source.replace('baremetal-diagnostic-init-002', 'baremetal-diagnostic-init-003')
    source = source.replace('native-diagnostic-init-002', 'native-diagnostic-init-003')
    source = source[:source.index("if __name__ == '__main__':")]
    namespace = {'__file__': str(base / 'prepare-baremetal-diagnostic-init-002.py')}
    exec(compile(source, 'packaging-003-adapter', 'exec'), namespace)
    generated = namespace['launcher_source']()
    ast.parse(generated)
    return generated


if __name__ == '__main__':
    exec(compile(launcher_source(), 'diagnostic-003-generated', 'exec'))
