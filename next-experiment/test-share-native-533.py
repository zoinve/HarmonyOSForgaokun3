"""Check532 integration and absence of the unsupported global config field."""
from pathlib import Path
import gzip
import runpy
import unittest

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'test-share-native-503.py').read_text()
    source=source.replace('commercial61-native-502','commercial61-native-532')
    source=source.replace('reports/share-supplicant-499','reports/share-supplicant-515')
    namespace=dict(__name__='share533_tests',__file__=str(BASE/'test-share-native-533.generated.py'))
    exec(compile(source,namespace['__file__'],'exec'),namespace)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(namespace['IntegrationTest'])
    result=unittest.TextTestRunner().run(suite)
    assert result.wasSuccessful() and result.testsRun==3
    parser=runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    entries={name:data for name,mode,data in parser(gzip.decompress(Path(
        '/home/zoinve/harmony-virgl-883/commercial61-native-532/minimal-overlay.img').read_bytes()))}
    assert b'update_config=' not in entries['native-target/share501/p2p.conf']
