"""Socket fixtures and strict ARM64 build; no controller/target access."""
from pathlib import Path
import runpy
import resource
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='bt453-') as directory:
        stage = Path(directory)
        source = runpy.run_path(str(BASE / 'native-bt-transport-451.py'))['broker451']()
        (stage / 'broker.c').write_text(source)
        subprocess.run(['aarch64-linux-gnu-gcc', '-O2', '-Wall', '-Wextra', '-Werror',
                        '-static', '-I', str(BASE), str(stage / 'broker.c'),
                        '-o', str(stage / 'broker')], check=True)
        subprocess.run(['gcc', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                        '-fsanitize=address,undefined', '-I', str(BASE), '-I', str(stage),
                        str(BASE / 'test-bt-transport-452.c'), '-pthread',
                        '-o', str(stage / 'test')], check=True)
        subprocess.run([str(stage / 'test')], check=True, timeout=15)
        old = runpy.run_path(str(BASE / 'test-bt-outcomes-437.py'))['broker435']()
        (stage / 'broker.c').write_text(old)
        subprocess.run(['gcc', '-O1', '-Wall', '-Wextra', '-Werror',
                        '-I', str(BASE), '-I', str(stage),
                        str(BASE / 'test-bt-transport-452.c'), '-pthread',
                        '-o', str(stage / 'old-test')], check=True)
        previous = subprocess.run([str(stage / 'old-test')], capture_output=True,
                                  timeout=15, preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_CORE, (0, 0)))
        assert previous.returncode != 0 and b'recv(h[1],actual' in previous.stderr
        print('BT453 old435_buffered_hangup_regression=reproduced')
        print('BT453 arm64_broker=pass physical_pairing=0')
