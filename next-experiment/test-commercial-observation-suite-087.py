"""Run unchanged helper/decoder regressions plus the original Dock audit tests."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'test-commercial-observation-suite-086.py').read_text()
source = source.replace('reports/commercial61-native-086/test-results.json',
                        'reports/commercial61-native-087/test-results.json')
anchor = "'test-commercial-oobe-decoder-079.py', 'test-trace-stream-admission-085.py')"
assert source.count(anchor) == 1
source = source.replace(anchor,
    "'test-commercial-oobe-decoder-079.py', 'test-trace-stream-admission-085.py', 'test-commercial-dock-literals-086.py')", 1)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
