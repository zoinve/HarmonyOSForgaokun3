"""Retain full-chain admission while requiring the exact USB protection guard."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'test-commercial-admission-174.py').read_text()
    source = source.replace('commercial61-native-174', 'commercial61-native-175')
    source = source.replace("('commercial61-native-166-compile-fix-1', 'commercial61-native-175')",
                            "('commercial61-native-166-compile-fix-1', 'commercial61-native-175-compile-fix-1')")
    source = source.replace('build-commercial-native-174.py', 'build-commercial-native-175.py')
    source = source.replace("generator['runtime174']", "generator['runtime175']")
    source = source.replace("generator['outer174']", "generator['outer175']")
    source = source.replace('commercial-workflow-174.py', 'commercial-workflow-175.py')
    source = source.replace("workflow['source174']", "workflow['source175']")
    source = source.replace('estimated174', 'estimated175')
    source = source.replace("tests=['test-native-usb-storage-174.py'", "tests=['test-usb-readonly-175.py','test-native-usb-storage-174.py'")
    source = source.replace('nineteen_focused_test_scripts_pass', 'twenty_focused_test_scripts_pass')
    anchor = "    assert (work/'init.c').read_text().count('native_usb_storage174_observe(child);')==2"
    assert source.count(anchor) == 1
    extra = '''
    guard=(BASE/'usb-readonly-175.h').read_bytes()
    assert sha(guard)==json.loads((report/'result.json').read_text())['usb175']['guard_sha256']
    assert sha((BASE/'native-usb-storage-174.h').read_bytes())==json.loads((report/'result.json').read_text())['usb175']['observer_sha256']
    init=(work/'init.c').read_text()
    assert init.count('if (native_usb_storage175_guard())return;')==1
    assert init.index('if (native_usb_storage175_guard())return;')<init.index('if(okay && persistent166_prepare())')
    assert 'O_RDWR' not in guard.decode() and 'O_WRONLY' not in guard.decode()
'''
    source = source.replace(anchor, anchor + '\n' + extra, 1)
    exec(compile(source, 'test-commercial-admission-175.generated.py', 'exec'),
         {'__name__':'__main__', '__file__':str(BASE / 'test-commercial-admission-175.generated.py')})
