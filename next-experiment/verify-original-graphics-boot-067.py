"""Independently check a longer observation, retaining actual outcomes and identities."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-066.py')))['source']
old = "number='066', tag='066'"
assert source.count(old) == 1
source = source.replace(old, "number='067', tag='067'")
old = '16 <= len(modes) <= 24'
assert source.count(old) == 1
source = source.replace(old, '16 <= len(modes) <= 48')
compile(source, 'independent-original-graphics-067', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-067', 'exec'))
