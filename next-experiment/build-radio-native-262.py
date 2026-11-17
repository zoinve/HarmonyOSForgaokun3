"""Place radio assets inside the actual target root; preserve unbooted261."""
from pathlib import Path
import json
import runpy

BASE = Path(__file__).resolve().parent
MODULE = runpy.run_path(str(BASE / 'build-radio-native-261.py'))


def outer262(source, old_digest, digest):
    value = MODULE['outer'](source, old_digest, digest)
    assert value.count('/commercial61-native-261/bootstrap-runtime087') == 5
    return value.replace('/commercial61-native-261/bootstrap-runtime087',
                         '/commercial61-native-262/bootstrap-runtime087')


if __name__ == '__main__':
    source = (BASE / 'build-radio-native-261.py').read_text()
    source = source[source.index("if __name__ == '__main__':"):]
    source = source.replace('commercial61-native-261', 'commercial61-native-262')
    old = '''        entries['radio261/hdf_devhost.cfg'] = (0o100644, config)
        for name in ['qca-broker', 'wifi-count', 'libbt_vendor.z.so']:
            entries['radio261/' + name] = (0o100755, (stage / name).read_bytes())'''
    new = '''        entries['native-target/radio261'] = (0o40755, b'')
        entries['native-target/radio261/hdf_devhost.cfg'] = (0o100644, config)
        entries['native-target/radio261/libbt_vendor.z.so'] = (0o100755, (stage / 'libbt_vendor.z.so').read_bytes())
        for name in ['qca-broker', 'wifi-count']:
            entries['radio261/' + name] = (0o100755, (stage / name).read_bytes())'''
    assert source.count(old) == 1
    source = source.replace(old, new, 1)
    env = dict(MODULE, __name__='__main__', outer=outer262)
    exec(compile(source, 'build-radio-native-262.generated.py', 'exec'), env)
    report = BASE.parent / 'reports/commercial61-native-261/withheld-262.json'
    report.open('x').write(json.dumps(dict(installed=False, booted=False,
        reason='261 placed bind sources outside the native-target root',
        replacement='262', original261_evidence_preserved=True), indent=2))
