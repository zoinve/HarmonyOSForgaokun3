"""Verify546's matching modules, corrected backend and private probe wiring."""
from pathlib import Path
import gzip
import runpy
import unittest

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'test-share-native-503.py').read_text()
    source=source.replace('commercial61-native-502','commercial61-native-546')
    source=source.replace('reports/share-supplicant-499','reports/share-supplicant-543')
    namespace=dict(__name__='compat548_tests',__file__=str(BASE/'test-compat-native-548.generated.py'))
    exec(compile(source,namespace['__file__'],'exec'),namespace)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(namespace['IntegrationTest'])
    result=unittest.TextTestRunner().run(suite)
    assert result.wasSuccessful() and result.testsRun==3
    parser=runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    work=Path('/home/zoinve/harmony-virgl-883/commercial61-native-546')
    entries={name:(mode,data) for name,mode,data in parser(gzip.decompress((work/'minimal-overlay.img').read_bytes()))}
    assert entries['native-target/compat525']==(0o40700,b'')
    assert b'update_config=' not in entries['native-target/share501/p2p.conf'][1]
    init=(work/'init.c').read_text()
    assert 'if(i==5 && started083)(void)network083_command(child,"compat-probe")' in init
    assert '!strcmp(mode,"compat-probe") ? 20' in init
    helper=runpy.run_path(str(BASE/'compat-network-helper-526.py'))['SOURCE']
    assert 'MSG_NOSIGNAL' in helper and 'MS_REC|MS_PRIVATE' in helper
