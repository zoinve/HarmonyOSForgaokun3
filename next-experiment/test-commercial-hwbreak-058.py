from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'test-commercial-hwbreak-052.py'))['source']
source = source.replace('commercial61-native-052', 'commercial61-native-058').replace('build-commercial-native-052.py', 'build-commercial-native-058.py').replace('commercial-hwbreak-052.py', 'commercial-hwbreak-058.py')
for old, new in [('record[96]', 'record[104]'), ('size=96', 'size=104'),
                 ('regs[7]={11,12,13,14,15,16,17}', 'regs[8]={11,12,13,14,15,16,17,18}'),
                 ('record+40,regs,56', 'record+40,regs,64'), ('i<96', 'i<104'), ('176', '184'),
                 ('200', '208'), ('205', '213'), ('sample_regs_user=0x7f', 'sample_regs_user=0x27f'),
                 ('seven real register fields', 'eight real register fields including x9')]:
    assert old in source, old
    source = source.replace(old, new)
specs = runpy.run_path(str(b / 'commercial-hwbreak-058.py'))['specifications']()
assert [row['event'] for row in specs] == ['frame_skip_result', 'screen_node_skip_result', 'processor_create_failed', 'processor_init_failed']
assert specs[-1]['virtual_address'] == '0x4205e8'
# Inject audited metadata only after converting the synthetic ring layout.
source = source.replace('synthetic_ring_tests_passed=True,', 'synthetic_ring_tests_passed=True, processing_specs_audited=True, eighth_register_x9_tested=True, processing_specifications=' + repr(specs) + ',')
source = source.replace('    tree = ast.parse(', "    assert b'x9=0x12' in result.stdout, result.stdout\n    tree = ast.parse(", 1)
source = source.replace('hwbreak-unit', 'hwbreak-unit-revision2').replace('hwbreak-test', 'hwbreak-test-revision2')
assert "'virtual_address': '0x4205e8'" in source
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
