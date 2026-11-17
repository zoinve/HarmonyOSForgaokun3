"""Require original complete files and successful export before pixel analysis."""
from pathlib import Path
import hashlib
import json
import re
import runpy

b = Path(__file__).resolve().parent
root = b.parent / 'reports/commercial61-native-068'
raw = root / 'runtime-evidence/raw'
manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
for name, item in manifest['files'].items():
    data = (raw / name).read_bytes()
    assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
ready = (raw / 'full-ready-068').read_bytes()
match = re.fullmatch(rb'FULL068_READY source_bytes=(\d+) output_bytes=(\d+) mono_us=(\d+) fb=(\d+)\n', ready)
assert match, 'No exact published full-frame marker'
source_bytes, output_bytes, mono_us, fb = map(int, match.groups())
assert 120000000 <= mono_us < 145000000 and fb > 0
phase = max(raw.glob('phase-*.log'), key=lambda p: int(p.stem.split('-')[1]))
assert re.search(rb'COMMERCIAL068_FULL_EXPORT child=\d+ status=0 deadline_ms=8000', phase.read_bytes())
stream_parser = runpy.run_path(str(b / 'analyze-commercial-presentation-066.py'))
streams = stream_parser['streams']((raw / 'interactive-faults030.log').read_bytes())
complete = [s for s in streams if s['eof'] == 1 and s['errno'] == 0]
assert complete
selected = max(complete, key=lambda s: (s['bytes'], s['sample']))
records = [dict((k.decode(), int(v)) for k, v in re.findall(rb'(\w+)=(-?\d+)', line))
           for line in selected['body'].splitlines() if line.startswith(b'COMMERCIAL068_FULL_FRAME ')]
assert len(records) == 1
record = records[0]
assert record['success'] == 1 and record['errno'] == 0 and record['mono_us'] == mono_us and record['fb'] == fb
assert record['source_bytes'] == source_bytes and record['output_bytes'] == output_bytes
helper = runpy.run_path(str(b / 'native-ppm-evidence-068.py'))
out = root / 'full-frame'
out.mkdir()
images = {}
views = {}
for name, expected in [('source', source_bytes), ('output', output_bytes)]:
    original = (raw / ('full-'+name+'-068.ppm')).read_bytes()
    assert len(original) == expected
    width, height, pixels = helper['parse_ppm'](original)
    if name == 'source':
        assert (width, height) == (record['source_w'], record['source_h'])
    else:
        assert (width, height) == (record['output_w'], record['output_h'])
    png = helper['png_bytes'](width, height, pixels)
    with (out / (name+'.png')).open('xb') as f:
        f.write(png)
    images[name] = dict(ppm_sha256=hashlib.sha256(original).hexdigest(),
                        png_sha256=hashlib.sha256(png).hexdigest(),
                        **helper['pixel_stats'](width, height, pixels))
    views[name] = (width, height, pixels)
sw, sh, source = views['source']
ow, oh, output = views['output']
different = None
if (ow, oh) == (sh, sw):
    different = sum(output[(y*ow+x)*3:(y*ow+x+1)*3] !=
                    source[((sh-1-x)*sw+y)*3:((sh-1-x)*sw+y+1)*3]
                    for y in range(oh) for x in range(ow))
result = dict(run=manifest['run'], verified_files=len(manifest['files']),
              full_resolution_files_complete=True, full_capture_record=record,
              export_status=0, images=images, clockwise_rotation_different_pixels=different,
              lossless_png_views=True, desktop_verified=False, interaction_verified=False)
with (root / 'full-frame-analysis.json').open('x') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
