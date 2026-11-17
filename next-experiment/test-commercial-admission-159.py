"""Add dynamic address/discovery and reproducible helper gates to native guards."""
from pathlib import Path
import runpy
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
BUILD = Path('/home/zoinve/harmony-virgl-883/commercial61-native-159')


if __name__ == '__main__':
    generated = (BUILD / 'live-debug-launcher-159.c').read_text()
    expected = runpy.run_path(str(BASE / 'build-commercial-native-159.py'))['helper_source159']()
    assert generated == expected
    for marker in ['live_address159_select','live_address159_config','discovery159_open("wlan0")',
        'sshd_config.live','live_root158_open','CLONE_NEWPID | CLONE_NEWNS | SIGCHLD']:
        assert marker in generated
    assert '192.168.10.210' not in generated and 'ADDRESS159' not in generated
    with tempfile.TemporaryDirectory(prefix='rebuild159-') as directory:
        binary = Path(directory) / 'launcher'
        result = subprocess.run(['aarch64-linux-gnu-gcc','-static','-Os','-s','-Wall','-Wextra','-Werror','-I',str(BASE),
            str(BUILD / 'live-debug-launcher-159.c'),'-o',str(binary)],capture_output=True,timeout=60)
        assert result.returncode == 0,result.stderr.decode()
        assert binary.read_bytes() == (BUILD / 'live-debug159').read_bytes()
    source = (BASE / 'test-commercial-admission-157.py').read_text().replace('157','159')
    source = source.replace('commercial61-native-153','commercial61-native-157')
    source = source.replace('reports/live-debug-inputs-159','reports/live-debug-inputs-157')
    source = source.replace("BASE / 'native-live-debug-159.h'","work / 'native-live-debug-159.h'")
    source = source.replace("BASE / 'live-debug-launcher-159.c'","work / 'live-debug-launcher-159.c'")
    source = source.replace('test-live-debug-launcher-159.py','test-live-debug-launcher-157.py')
    source = source.replace("'test-live-debug-reader-156.py',","'test-live-debug-analysis-159.py','test-live-debug-root-158.py','test-live-debug-address-159.py','test-live-debug-discovery-159.py','test-live-debug-reader-156.py',",1)
    exec(compile(source,'test-commercial-admission-159.generated.py','exec'),
        {'__name__':'__main__','__file__':str(BASE / 'test-commercial-admission-159.generated.py')})
