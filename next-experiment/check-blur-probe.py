"""The diagnostic may change exactly one cosmetic setting in the RAM config."""
from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
transform = runpy.run_path(str(base / 'blur-probe.py'))['disable_blur']
source = (base / 'init.c').read_text()
result = transform(source)
added = r'\"setparam persist.sys.graphic.blurEnabled 0\", '
assert result.count(added) == 1
assert result.replace(added, '', 1) == source
assert result.index('load_persist_params') < result.index(added)
try:
    transform('missing anchor')
except AssertionError:
    pass
else:
    raise AssertionError('missing config anchor must be rejected')
print('PASS: exactly one cosmetic blur setting; all other boot code unchanged')
