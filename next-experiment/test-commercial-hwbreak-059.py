from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'test-commercial-hwbreak-058.py'))['source']
old_specs = runpy.run_path(str(b / 'commercial-hwbreak-058.py'))['specifications']()
new_specs = runpy.run_path(str(b / 'commercial-hwbreak-059.py'))['specifications']()
assert repr(old_specs) in source
source = source.replace(repr(old_specs), repr(new_specs), 1)
for old, new in [('commercial61-native-058', 'commercial61-native-059'),
                 ('build-commercial-native-058.py', 'build-commercial-native-059.py'),
                 ('commercial-hwbreak-058.py', 'commercial-hwbreak-059.py')]:
    source = source.replace(old, new)
source = source.replace("assert changed == ['init'], changed", "assert sorted(changed) == sorted(['init', 'native-target/graphics016/sys_prod/etc/param/hw_defaults.para']), changed")
source = source.replace('original_userland_byte_identical', 'original_userland_binaries_byte_identical')
anchor = "    manifest = dict("
test = '''    key = 'native-target/graphics016/sys_prod/etc/param/hw_defaults.para'
    assert old[key][0] == new[key][0]
    assert new[key][1] == old[key][1] + b'rosen.uni.partialrender.enabled=0\\n'
    assert b'rosen.uni.partialrender.enabled' not in old[key][1]
'''
assert source.count(anchor) == 1
source = source.replace(anchor, test + anchor, 1)
source = source.replace('synthetic_ring_tests_passed=True,', 'synthetic_ring_tests_passed=True, public_parameter_only_change_tested=True,')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
