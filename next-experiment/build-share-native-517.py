"""Use the file-log-capable P2P binary; retain the tested kernel/module bundle."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'build-share-native-502.py').read_text()
    assert source.count('reports/share-supplicant-499/result.json') == 1
    source = source.replace('reports/share-supplicant-499/result.json',
                            'reports/share-supplicant-515/result.json')
    source = source.replace('commercial61-native-502', 'commercial61-native-517')
    assert source.count('        502, original') == 1
    source = source.replace('        502, original', '        517, original')
    # Preserve the previous source functions and their distinct diagnostic tags.
    exec(compile(source, str(BASE / 'build-share-native-517.generated.py'), 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'build-share-native-517.generated.py')))
