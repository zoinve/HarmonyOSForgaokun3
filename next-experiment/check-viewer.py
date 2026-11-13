"""Check real GTK-VNC sizing policy without connecting or opening a visible window."""
import sys
from pathlib import Path

path = Path(sys.argv[1])
sys.argv = [str(path), '/unused-test-socket']
source = path.read_text()
ns = {'__file__': str(path)}
exec(compile(source[:source.index('window.show_all()')], str(path), 'exec'), ns)
display = ns['display']
assert display.get_scaling(), '1080p guest must fit smaller HiDPI logical viewport'
assert display.get_keep_aspect_ratio(), 'fit must preserve aspect ratio, not stretch'
assert not display.get_read_only(), 'viewer must forward input'
assert display.get_pointer_grab(), 'relative USB mouse requires viewer pointer capture'
print('PASS: real GTK-VNC aspect-preserving fit and interactive input policy')
