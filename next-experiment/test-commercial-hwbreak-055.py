from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'test-commercial-hwbreak-052.py'))['source']
source = source.replace('commercial61-native-052', 'commercial61-native-055').replace('build-commercial-native-052.py', 'build-commercial-native-055.py').replace('commercial-hwbreak-052.py', 'commercial-hwbreak-055.py')
specs = runpy.run_path(str(b / 'commercial-hwbreak-055.py'))['specifications']()
assert [row['event'] for row in specs] == ['command_execute', 'screen_skip_result', 'worker_sync', 'worker_render']
source = source.replace('synthetic_ring_tests_passed=True,', 'synthetic_ring_tests_passed=True, processing_specs_audited=True, processing_specifications=' + repr(specs) + ',')
# Preserve the first attempt's offline output after its import-contract failure.
source = source.replace('hwbreak-unit', 'hwbreak-unit-importfix')
source = source.replace('hwbreak-test-compile.stderr', 'hwbreak-test-importfix-compile.stderr').replace('hwbreak-test.stdout', 'hwbreak-test-importfix.stdout')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
