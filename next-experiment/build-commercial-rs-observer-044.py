"""Keep the 043 build ABI and original methods; replace only the Binder observer."""
from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
source = (base / 'build-commercial-rs-observer-043.py').read_text().replace('043', '044')
anchor = "(base / 'next-experiment/commercial-binder-observer-044.h').read_text()"
assert source.count(anchor) == 1
source = source.replace(anchor, "runpy.run_path(str(base / 'next-experiment/commercial-binder-observer-044.py'))['source']()", 1)
source = source.replace('ioctl_stage_log_limit_per_process=264', 'ioctl_stage_log_limit_per_process=396')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
