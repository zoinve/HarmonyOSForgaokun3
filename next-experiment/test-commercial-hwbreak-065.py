from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'test-commercial-hwbreak-064.py'))['source']
source = source.replace('commercial61-native-064', 'commercial61-native-065').replace('build-commercial-native-064.py', 'build-commercial-native-065.py')
source = source.replace("['init', 'native-target/desktop-order020.sh']", "['init', 'native-target/bootstrap', 'native-target/desktop-order020.sh']")
source = source.replace("sorted(['init', 'native-target/graphics016", "sorted(['init', 'native-target/bootstrap', 'native-target/graphics016")
anchor = '    module = runpy.run_path'
extra = '''    previous064 = helpers['parse'](ROOT / 'commercial61-native-064/initrd.img')
    changed064 = sorted(name for name in new if new[name] != previous064[name])
    assert set(previous064) == set(new)
    assert changed064 == ['init', 'native-target/bootstrap'], changed064
    layout = runpy.run_path(str(BASE / 'next-experiment/commercial-root-layout-065.py'))
    candidate = runpy.run_path(str(BASE / 'next-experiment/build-commercial-native-065.py'))
    previous_module = runpy.run_path(str(BASE / 'next-experiment/build-commercial-native-064.py'))
    assert candidate['inner'] == layout['repair'](previous_module['inner'])
    subprocess.run(['python3', str(BASE / 'next-experiment/test-commercial-root-layout-065.py')], check=True)
'''
assert source.count(anchor) == 1
source = source.replace(anchor, extra + anchor, 1)
source = source.replace('original_bootstrap_byte_identical=True', 'original_bootstrap_byte_identical=False, bootstrap_only_original_layout_alias_added=True, exact_delta_from_064=changed064')
source = source.replace('public_parameter_and_account_order_only_change_tested=True', 'public_parameter_account_and_root_layout_delta_tested=True')
source = source.replace('hwbreak-test-revision2', 'hwbreak-test-revision3').replace('hwbreak-unit-revision2', 'hwbreak-unit-revision3')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
