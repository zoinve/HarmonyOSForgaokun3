"""Correct vendor image root; preserve the incomplete first audit."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = (b / 'audit-commercial-event-declarations-063.py').read_text()
assert source.count("('vendor', 'p109-vendor.kr990-ext4-v1.img', '/vendor')") == 1
source = source.replace("('vendor', 'p109-vendor.kr990-ext4-v1.img', '/vendor')",
                        "('vendor', 'p109-vendor.kr990-ext4-v1.img', '')")
source = source.replace("'reports/commercial-event-declarations-063'",
                        "'reports/commercial-event-declarations-063-r2'")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
