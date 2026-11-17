from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'test-commercial-hwbreak-062.py'))['source']
source = source.replace('commercial61-native-062', 'commercial61-native-063').replace('build-commercial-native-062.py', 'build-commercial-native-063.py')
source = source.replace('commercial-desktop-order-062.py', 'commercial-account-order-063.py').replace('test-commercial-desktop-order-062.py', 'test-commercial-account-order-063.py')
anchor = "    module = runpy.run_path"
extra = '''    previous062 = helpers['parse'](ROOT / 'commercial61-native-062/initrd.img')
    assert set(previous062) == set(new)
    assert sorted(name for name in new if new[name] != previous062[name]) == ['init', 'native-target/desktop-order020.sh']
    helper063 = runpy.run_path(str(BASE / 'next-experiment/commercial-account-order-063.py'))
    assert '/proc/%d/root' + helper063['LOG'] in runpy.run_path(str(BASE / 'next-experiment/build-commercial-native-063.py'))['outer']
'''
assert source.count(anchor) == 1
source = source.replace(anchor, extra + anchor, 1)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
