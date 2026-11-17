"""Retain prior binary/perf checks and prove 064 has only diagnostic changes."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'test-commercial-hwbreak-063.py'))['source']
source = source.replace('commercial61-native-063', 'commercial61-native-064').replace('build-commercial-native-063.py', 'build-commercial-native-064.py')
source = source.replace("str(BASE / 'next-experiment/commercial-account-order-063.py'))['repair']", "str(BASE / 'next-experiment/commercial-event-state-064.py'))['repair']")
anchor = '    module = runpy.run_path'
extra = '''    previous063 = helpers['parse'](ROOT / 'commercial61-native-063/initrd.img')
    assert set(previous063) == set(new)
    changed063 = sorted(name for name in new if new[name] != previous063[name])
    assert changed063 == ['init', 'native-target/desktop-order020.sh'], changed063
    event064 = runpy.run_path(str(BASE / 'next-experiment/commercial-event-state-064.py'))
    assert '/proc/%d/root' + event064['LOG'] in runpy.run_path(str(BASE / 'next-experiment/build-commercial-native-064.py'))['outer']
    subprocess.run(['python3', str(BASE / 'next-experiment/test-commercial-event-state-064.py')], check=True)
'''
assert source.count(anchor) == 1
source = source.replace(anchor, extra + anchor, 1)
source = source.replace('synthetic_ring_tests_passed=True,', 'synthetic_ring_tests_passed=True, public_event_diagnostics_tested=True, exact_delta_from_063=changed063,')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
