"""Reconstruct all archives and reproducibly rebuild the teardown candidate."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'test-commercial-admission-166.py').read_text()
    replacements = [
        ('commercial61-native-166-compile-fix-1', 'commercial61-native-172'),
        ('commercial61-native-166', 'commercial61-native-172'),
        ('build-commercial-native-166.py', 'build-commercial-native-172.py'),
        ("generator['runtime166']", "generator['runtime172']"),
        ("generator['outer166']", "generator['outer172']"),
        ("['persistent-data-166.h','persistent-runtime-166.h']", "['persistent-data-172.h','persistent-runtime-168.h']"),
        ('commercial-workflow-166.py', 'commercial-workflow-172.py'),
        ("workflow['source166']", "workflow['source172']"),
        ('estimated166', 'estimated172'),
        ("tests=['test-persistent-data-166.py',", "tests=['test-persistent-lifecycle-172.py','test-persistent-runtime-168.py','test-persistent-data-166.py',"),
        ('fifteen_focused_test_scripts_pass', 'seventeen_focused_test_scripts_pass'),
    ]
    for old, new in replacements:
        assert old in source, old
        source = source.replace(old, new)
    exec(compile(source, 'test-commercial-admission-172.generated.py', 'exec'),
        {'__name__': '__main__', '__file__': str(BASE / 'test-commercial-admission-172.generated.py')})
