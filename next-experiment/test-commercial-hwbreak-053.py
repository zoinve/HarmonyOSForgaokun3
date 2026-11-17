from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'test-commercial-hwbreak-052.py'))['source']
source = source.replace('commercial61-native-052', 'commercial61-native-053').replace('build-commercial-native-052.py', 'build-commercial-native-053.py').replace('commercial-hwbreak-052.py', 'commercial-hwbreak-053.py')
source = source.replace('synthetic_ring_tests_passed=True,', 'synthetic_ring_tests_passed=True, processing_specs_audited=True,')
specs = runpy.run_path(str(b / 'commercial-hwbreak-053.py'))['specifications']()
assert [row['event'] for row in specs] == ['unmarshal_result', 'recv_data', 'process_data', 'process_uni']
source = source.replace('processing_specs_audited=True,', 'processing_specs_audited=True, processing_specifications=' + repr(specs) + ',')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
