from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-054.py')))['payload']
payload = payload.replace('commercial61-native-054', 'commercial61-native-059').replace('COMMERCIAL054', 'COMMERCIAL059').replace('ordered_chain_equals_full_054', 'ordered_chain_equals_full_059')
anchor = "assert set(patch)=={'init',"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "assert set(patch)=={'native-target/graphics016/sys_prod/etc/param/hw_defaults.para','init',", 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
