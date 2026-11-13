"""The observer changes only diagnostic capture, never rendering or services."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
transform=runpy.run_path(str(base/'gpu-frame-observer.py'))['frame_observer']
source=(base/'gpu-present-snapshot.h').read_text()
result=transform(source)
assert 'O_RDONLY|O_CLOEXEC' in result
assert 'O_EXCL|O_NOFOLLOW|O_CLOEXEC' in result
assert 'O_TRUNC' not in result
assert 'i<90' in result and 'sleep(15)' in result
assert 'rename(' in result and 'gpu913-capture/latest.ppm' in result
assert 'chmod(' not in result and 'kill(' not in result
assert source.replace('/data/local/tmp/gpu898-frame.ppm','/data/local/tmp/gpu913-capture/pending.ppm') in result
print('PASS: bounded read-only framebuffer observer, atomic private output')
