from pathlib import Path

source = Path(__file__).with_name('test-commercial-workflow-050.py').read_text()
source = source.replace('commercial-workflow-050.py', 'commercial-workflow-066.py').replace('source050', 'source066').replace('commercial61-native-050', 'commercial61-native-066').replace('build-commercial-native-050.py', 'build-commercial-native-066.py').replace('COMMERCIAL050', 'COMMERCIAL066')
old = "assert p['inner'] == runpy.run_path(str(b / 'build-commercial-native-045.py'))['inner']"
new = "assert p['inner'] == runpy.run_path(str(b / 'commercial-perf-stream-066.py'))['repair'](runpy.run_path(str(b / 'build-commercial-native-065.py'))['inner'])"
assert source.count(old) == 1
source = source.replace(old, new, 1).replace('unchanged original bootstrap', 'exact bounded read-only trace change')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
