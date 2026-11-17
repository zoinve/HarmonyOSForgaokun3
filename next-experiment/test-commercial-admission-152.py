"""Reuse the established full-chain gate with explicit 152/148 substitutions."""
from pathlib import Path

BASE = Path(__file__).resolve().parent


if __name__ == '__main__':
    source = (BASE / 'test-commercial-admission-148.py').read_text()
    changes = [
        ("report = ROOT / 'reports/commercial61-native-148'", "report = ROOT / 'reports/commercial61-native-152'"),
        ("BUILD / 'commercial61-native-148', BUILD / 'commercial61-native-145'", "BUILD / 'commercial61-native-152', BUILD / 'commercial61-native-148'"),
        ('[(parent, 145), (work, 148)]', '[(parent, 148), (work, 152)]'),
        ('build-commercial-native-148.py', 'build-commercial-native-152.py'),
        ('native-input-usb-148.h', 'native-service-devices-152.h'),
        ("metadata['inputusb148']", "metadata['inputusb152']"),
        ("for test in ['test-native-input-usb-148.py',", "for test in ['test-native-service-devices-152.py', 'test-native-input-usb-148.py',"),
        ('commercial-workflow-148.py', 'commercial-workflow-152.py'),
        ("workflow['source148']", "workflow['source152']"),
        ('estimated148<1800', 'estimated152<1800'),
    ]
    for old, new in changes:
        assert old in source, old
        source = source.replace(old, new)
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
