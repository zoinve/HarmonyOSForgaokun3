"""Build fresh 881 from the retained read-only probe with only blur disabled."""
from pathlib import Path
import runpy
import subprocess

base = Path(__file__).resolve().parent
builder = (base / 'build-command-probe.py').read_text()
start = builder.index("source = (base / 'init.c').read_text()")
end = builder.index('out.mkdir()')
replacement = '''import runpy
source = runpy.run_path(str(base / 'blur-probe.py'))['disable_blur'](
    (base / 'payload-876' / 'init.c').read_text())
'''
builder = builder[:start] + replacement + builder[end:]
builder = builder.replace('payload-873', 'payload-881').replace('command-probe-873', 'command-probe-881')
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-881'
assert not (base / 'payload-881').exists()
subprocess.run(['ssh', 'matebook', 'mkdir ' + remote], check=True)
exec(compile(builder, str(base / 'build-command-probe.py'), 'exec'), {'__file__': str(base / 'build-command-probe.py')})
