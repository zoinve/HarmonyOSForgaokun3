"""New run's bounded read-only collection, reusing the measured HiLog exception."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('retrieve-native-presentation-043-attempt-002.py')))['source']
for old, new in [('native-original-graphics-boot-043', 'native-original-graphics-boot-044'),
                 ('native-interactive-043-', 'native-interactive-044-'),
                 ('/mnt/harmony-return-audit-043-attempt-002', '/mnt/harmony-return-audit-044')]:
    assert old in source, old
    source = source.replace(old, new)
compile(source, 'bounded-native044-retrieval', 'exec')
scope = {'__name__': __name__, '__file__': __file__}
exec(compile(source, 'bounded-native044-retrieval', 'exec'), scope)
REMOTE = scope['REMOTE']
file_limit = scope['file_limit']
validate_members = scope['validate_members']
