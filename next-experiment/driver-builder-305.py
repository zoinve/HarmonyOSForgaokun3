"""Reuse the bounded radio baseline with explicit per-candidate transformations."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent

def build(number, runtime, outer, vendor, extra):
    module = runpy.run_path(str(BASE / 'build-radio-native-261.py'))
    once = module['once']
    source = (BASE / 'build-radio-native-261.py').read_text()
    source = source[source.index('if __name__ == '):]
    source = source.replace('commercial61-native-261', 'commercial61-native-' + str(number))
    source = once(source, '        stage = Path(tmp)', '''        stage = Path(tmp)
        for header in ['persistent-data-166.h', 'persistent-data-172.h', 'persistent-unmount-plan-201.h', 'native-live-debug-159.h']:
            os.link(parent / header, stage / header)''')
    source = once(source, '        vendor = once(vendor,', '        vendor = vendor_transform(vendor)\n        vendor = once(vendor,')
    # This endpoint must remain inside the original chipset sandbox's vendor view.
    source = source.replace(repr('/native-bt-broker.sock'), repr('/vendor/lib64/harmony-graphics/native-bt-broker.sock'))
    source = once(source, '''        entries['radio261/hdf_devhost.cfg'] = (0o100644, config)
        for name in ['qca-broker', 'wifi-count', 'libbt_vendor.z.so']:
            entries['radio261/' + name] = (0o100755, (stage / name).read_bytes())''', '''        entries['native-target/radio261'] = (0o40755, b'')
        entries['native-target/radio261/hdf_devhost.cfg'] = (0o100644, config)
        entries['native-target/radio261/libbt_vendor.z.so'] = (0o100755, (stage / 'libbt_vendor.z.so').read_bytes())
        for name in ['qca-broker', 'wifi-count']:
            entries['radio261/' + name] = (0o100755, (stage / name).read_bytes())''')
    source = once(source, '        raw = b', '        extra_assets(compile_program, stage, entries)\n        raw = b')
    exec(compile(source, 'driver-builder-305.generated.py', 'exec'),
         dict(module, __name__='__main__', runtime=runtime, outer=outer,
              vendor_transform=vendor, extra_assets=extra))
