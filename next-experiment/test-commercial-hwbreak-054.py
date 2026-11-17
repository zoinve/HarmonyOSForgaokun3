from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'test-commercial-hwbreak-052.py'))['source']
source = source.replace('commercial61-native-052', 'commercial61-native-054').replace('build-commercial-native-052.py', 'build-commercial-native-054.py').replace('commercial-hwbreak-052.py', 'commercial-hwbreak-054.py')
source = source.replace('synthetic_ring_tests_passed=True,', 'synthetic_ring_tests_passed=True, processing_specs_audited=True,')
specs = runpy.run_path(str(b / 'commercial-hwbreak-054.py'))['specifications']()
assert [row['event'] for row in specs] == ['transaction_process', 'process_command', 'render', 'uni_render']
source = source.replace('processing_specs_audited=True,', 'processing_specs_audited=True, processing_specifications=' + repr(specs) + ',')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
