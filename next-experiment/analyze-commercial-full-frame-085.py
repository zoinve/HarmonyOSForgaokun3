"""Verify and render original full-resolution captured pixels from085."""
from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-full-frame-068.py').read_text().replace(
    'reports/commercial61-native-068', 'reports/commercial61-native-085').replace(
    'COMMERCIAL068_FULL_EXPORT', 'COMMERCIAL085_FULL_EXPORT')
anchor = "streams = stream_parser['streams']((raw / 'interactive-faults030.log').read_bytes())"
assert source.count(anchor) == 1
source = source.replace(anchor, """audit085 = runpy.run_path(str(b / 'trace-stream-admission-085.py'))['inspect_streams']((raw / 'interactive-faults030.log').read_bytes())
streams = audit085['valid']
with (root / 'trace-stream-admission.json').open('x') as stream:
    json.dump(dict(rejected_streams=audit085['rejected'], valid_streams=[{k:v for k,v in row.items() if k!='body'} for row in streams], rejected_streams_not_used_as_capture_evidence=True), stream, indent=2)""", 1)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
