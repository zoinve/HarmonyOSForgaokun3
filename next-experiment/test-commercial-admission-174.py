"""Require original runtime preservation and the full archive-chain checks."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'test-commercial-admission-166.py').read_text()
    replacements = [
        ('commercial61-native-166-compile-fix-1', 'commercial61-native-174'),
        ('commercial61-native-166', 'commercial61-native-174'),
        ('build-commercial-native-166.py', 'build-commercial-native-174.py'),
        ("generator['runtime166']", "generator['runtime174']"),
        ("generator['outer166']", "generator['outer174']"),
        ("['persistent-data-166.h','persistent-runtime-166.h']", "['persistent-data-172.h','persistent-runtime-173.h']"),
        ('commercial-workflow-166.py', 'commercial-workflow-174.py'),
        ("workflow['source166']", "workflow['source174']"),
        ('estimated166', 'estimated174'),
        ("tests=['test-persistent-data-166.py',", "tests=['test-native-usb-storage-174.py','test-persistent-runtime-173.py','test-persistent-lifecycle-172.py','test-persistent-runtime-168.py','test-persistent-data-166.py',"),
        ('fifteen_focused_test_scripts_pass', 'nineteen_focused_test_scripts_pass'),
    ]
    for old, new in replacements:
        assert old in source, old
        source = source.replace(old, new)
    anchor = "    metadata=json.loads((report/'result.json').read_text())"
    assert source.count(anchor) == 1
    extra = '''
    previous=BUILD/'commercial61-native-173'
    assert (work/'bootstrap-runtime087').read_bytes()==(previous/'bootstrap-runtime087').read_bytes()
    assert (work/'bootstrap-runtime087.c').read_bytes()==(previous/'bootstrap-runtime087.c').read_bytes()
    header=(BASE/'native-usb-storage-174.h').read_text()
    for forbidden in ['mknod(', 'mount(', 'BLKROSET', 'O_RDWR', 'O_WRONLY', '/serial', 'fsck.ntfs", NULL']:
        assert forbidden not in header,forbidden
    assert (work/'init.c').read_text().count('native_usb_storage174_observe(child);')==2
'''
    source = source.replace(anchor, extra + '\n' + anchor, 1)
    exec(compile(source, 'test-commercial-admission-174.generated.py', 'exec'),
         {'__name__':'__main__', '__file__':str(BASE / 'test-commercial-admission-174.generated.py')})
