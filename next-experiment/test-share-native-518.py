"""Apply the original integration guards to candidate517 and its corrected binary."""
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'test-share-native-503.py').read_text()
    source = source.replace('commercial61-native-502', 'commercial61-native-517')
    source = source.replace('reports/share-supplicant-499', 'reports/share-supplicant-515')
    namespace = dict(__name__='share518_tests',
                     __file__=str(BASE / 'test-share-native-518.generated.py'))
    exec(compile(source, namespace['__file__'], 'exec'), namespace)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(namespace['IntegrationTest'])
    result = unittest.TextTestRunner().run(suite)
    raise SystemExit(0 if result.wasSuccessful() and result.testsRun == 3 else 1)
