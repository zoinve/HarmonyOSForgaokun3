"""Sanitized fixture tests for new capture paths; no target or hardware access."""
from pathlib import Path
import runpy
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
HEADERS = Path('/home/zoinve/harmony-virgl-883/audio-contract-314-peripheral/audio/interfaces/sound/v1_0')

if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='audio418-') as directory:
        stage = Path(directory)
        (stage/'vendor.c').write_text(runpy.run_path(str(BASE/'native-audio-vdi-414.py'))['vendor414']())
        (stage/'server.c').write_text(runpy.run_path(str(BASE/'native-audio-server-411.py'))['server411']())
        flags = ['-O1', '-g', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
                 '-I', str(stage), '-I', str(BASE), '-I', str(HEADERS)]
        for number, name in [(416, 'card'), (417, 'capture'), (419, 'backend')]:
            executable = stage/name
            subprocess.run(['gcc', *flags, str(BASE/f'test-audio-{name}-{number}.c'),
                            '-pthread', '-lm', '-ldl', '-o', str(executable)], check=True)
            subprocess.run([str(executable)], check=True, timeout=15)
