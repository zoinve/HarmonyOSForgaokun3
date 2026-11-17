"""Preserve observation tests and verify the one account-order script change."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'test-commercial-hwbreak-061.py'))['source']
source = source.replace('commercial61-native-061', 'commercial61-native-062').replace('build-commercial-native-061.py', 'build-commercial-native-062.py')
old = "['init', 'native-target/graphics016/sys_prod/etc/param/hw_defaults.para']"
new = "['init', 'native-target/graphics016/sys_prod/etc/param/hw_defaults.para', 'native-target/desktop-order020.sh']"
assert source.count(old) == 1
source = source.replace(old, new, 1)
anchor = "    module = runpy.run_path"
extra = '''    baseline = helpers['parse'](ROOT / 'commercial61-native-061/initrd.img')
    changed061 = [name for name in baseline if baseline[name] != new[name]]
    assert sorted(changed061) == ['init', 'native-target/desktop-order020.sh'], changed061
    original = (report / 'original-account-order.sh').read_text()
    patched = runpy.run_path(str(BASE / 'next-experiment/commercial-desktop-order-062.py'))['repair'](original)
    assert new['native-target/desktop-order020.sh'][1] == patched.encode()
    assert baseline['native-target/desktop-order020.sh'][0] == new['native-target/desktop-order020.sh'][0]
    subprocess.run(['sh', '-n'], input=patched, text=True, check=True)
    subprocess.run(['python3', str(BASE / 'next-experiment/test-commercial-desktop-order-062.py')], check=True)
'''
assert source.count(anchor) == 1
source = source.replace(anchor, extra + anchor, 1)
source = source.replace('public_parameter_only_change_tested=True', 'public_parameter_and_account_order_only_change_tested=True, account_order_tests_passed=True, exact_delta_from_061=changed061')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
