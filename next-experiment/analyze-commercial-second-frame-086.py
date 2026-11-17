"""Apply the full byte/record checks to the independently captured140s frame."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'analyze-commercial-full-frame-086.py'))['source']
for old, new in (('full-ready-068', 'full-ready-075'),
                 ('120000000 <= mono_us < 145000000', '140000000 <= mono_us < 165000000'),
                 ('COMMERCIAL086_FULL_EXPORT', 'COMMERCIAL086_SECOND_FULL_EXPORT'),
                 ('COMMERCIAL068_FULL_FRAME', 'COMMERCIAL075_FULL_FRAME'),
                 ("name+'-068.ppm'", "name+'-075.ppm'"),
                 ("root / 'full-frame'", "root / 'second-full-frame'"),
                 ('full-frame-analysis.json', 'second-full-frame-analysis.json'),
                 ('trace-stream-admission.json', 'trace-stream-admission-second.json')):
    assert old in source
    source = source.replace(old, new)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
