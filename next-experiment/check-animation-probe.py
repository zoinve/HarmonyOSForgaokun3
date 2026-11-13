"""Verify the next RAM probe changes only animation scale plus read-only queries."""
from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
source = (base / 'payload-881' / 'init.c').read_text()
transform = runpy.run_path(str(base / 'animation-probe.py'))['disable_animation']
result = transform(source)
added = '\\"setparam persist.sys.graphic.animationscale 0\\", '
query = '    lab_shell_run("render-parameters","/system/bin/param get persist.sys.graphic.blurEnabled; /system/bin/param get persist.sys.graphic.animationscale",10,"/system/bin/sh");\n'
assert result.count(added) == 1
assert result.count(query) == 1
assert result.replace(added, '', 1).replace(query, '', 1) == source
try:
    transform('no configuration anchor')
except AssertionError:
    pass
else:
    raise AssertionError('missing anchors must be rejected')
print('PASS: only cosmetic animation scale and read-only parameter queries added')
