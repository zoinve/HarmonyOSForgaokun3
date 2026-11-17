"""Rebuild the full original-service chain with lifecycle and history fixes."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'test-commercial-admission-166.py').read_text()
    replacements = [
        ('commercial61-native-166-compile-fix-1','commercial61-native-173'),
        ('commercial61-native-166','commercial61-native-173'),
        ('build-commercial-native-166.py','build-commercial-native-173.py'),
        ("generator['runtime166']","generator['runtime173']"),
        ("generator['outer166']","generator['outer173']"),
        ("['persistent-data-166.h','persistent-runtime-166.h']","['persistent-data-172.h','persistent-runtime-173.h']"),
        ('commercial-workflow-166.py','commercial-workflow-173.py'),
        ("workflow['source166']","workflow['source173']"),
        ('estimated166','estimated173'),
        ("tests=['test-persistent-data-166.py',","tests=['test-persistent-runtime-173.py','test-persistent-lifecycle-172.py','test-persistent-runtime-168.py','test-persistent-data-166.py',"),
        ('fifteen_focused_test_scripts_pass','eighteen_focused_test_scripts_pass'),
    ]
    for old,new in replacements:
        assert old in source,old
        source = source.replace(old,new)
    exec(compile(source,'test-commercial-admission-173.generated.py','exec'),
        {'__name__':'__main__','__file__':str(BASE / 'test-commercial-admission-173.generated.py')})
