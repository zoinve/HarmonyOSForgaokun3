"""Reuse sidecar admission and add absolute-root regression/reproducible build."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
BUILD = Path('/home/zoinve/harmony-virgl-883/commercial61-native-158')


if __name__ == '__main__':
    result = subprocess.run(['python3',str(BASE / 'test-live-debug-root-158.py')],capture_output=True,timeout=15)
    assert result.returncode == 0,result.stderr.decode()
    with tempfile.TemporaryDirectory(prefix='rebuild158-') as directory:
        binary = Path(directory) / 'launcher'
        result = subprocess.run(['aarch64-linux-gnu-gcc','-static','-Os','-s','-Wall','-Wextra','-Werror','-I',str(BASE),
            str(BUILD / 'live-debug-launcher-158.c'),'-o',str(binary)],capture_output=True,timeout=60)
        assert result.returncode == 0,result.stderr.decode()
        assert binary.read_bytes() == (BUILD / 'live-debug158').read_bytes(),'helper source/header rebuild mismatch'
    source = (BASE / 'test-commercial-admission-157.py').read_text().replace('157','158')
    source = source.replace('commercial61-native-153','commercial61-native-157')
    source = source.replace('reports/live-debug-inputs-158','reports/live-debug-inputs-157')
    source = source.replace("BASE / 'native-live-debug-158.h'","work / 'native-live-debug-158.h'")
    source = source.replace("BASE / 'live-debug-launcher-158.c'","work / 'live-debug-launcher-158.c'")
    source = source.replace('test-live-debug-launcher-158.py','test-live-debug-launcher-157.py')
    source = source.replace("'test-live-debug-reader-156.py',","'test-live-debug-root-158.py','test-live-debug-reader-156.py',",1)
    exec(compile(source,'test-commercial-admission-158.generated.py','exec'),
        {'__name__':'__main__','__file__':str(BASE / 'test-commercial-admission-158.generated.py')})
