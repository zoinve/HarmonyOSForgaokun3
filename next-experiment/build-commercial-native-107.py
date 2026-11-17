"""Reuse the sealed builder with an event-triggered, two-service observer."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE / 'build-commercial-native-105.py').read_text()
old = "    assert observer.index(b'/system/bin/timeout 12 /reference-stack-probe103') < observer.index(b'for task105 in ')"
assert source.count(old) == 1
source = source.replace(old, "    assert observer.index(b'SERVER107_QUERY_EVENT') < observer.index(b'SERVER107_DFX_CALL_BEGIN')")
for scope in ('commercial61-native-', 'commercial-server-stack-', 'commercial-server-stack', 'server_stack', 'observer'):
    source = source.replace(scope + '105', scope + '__NEW__').replace(scope + '104', scope + '105').replace(scope + '__NEW__', scope + '107')
source = source.replace('DFX call before proc survey; explicit call timing markers',
                        'Original query event triggers DeviceManager then CollaborationFwk DFX; no fixed guide delay')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
