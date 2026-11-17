"""Compile duplex candidates without installing or accessing microphone hardware."""
from pathlib import Path
import runpy
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
BUILD = Path('/home/zoinve/harmony-virgl-883')

if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='audio415-') as directory:
        stage = Path(directory)
        server = runpy.run_path(str(BASE/'native-audio-server-411.py'))['server411']()
        vendor = runpy.run_path(str(BASE/'native-audio-vdi-414.py'))['vendor414']()
        (stage/'server.c').write_text(server)
        (stage/'vendor.c').write_text(vendor)
        flags = ['-O2', '-Wall', '-Wextra', '-Werror', '-I', str(BASE)]
        subprocess.run(['aarch64-linux-gnu-gcc', *flags, str(stage/'server.c'),
                        '-ldl', '-pthread', '-o', str(stage/'server')], check=True)
        subprocess.run([str(BUILD/'window-bridge/toolchain/ohos-cc'), *flags,
                        '-shared', '-fPIC', '-Wl,--no-undefined', '-I',
                        str(BUILD/'audio-contract-314-peripheral/audio/interfaces/sound/v1_0'),
                        str(stage/'vendor.c'), '-o', str(stage/'vendor.so')], check=True)
        print('AUDIO415 arm64_server=pass official_vdi_build=pass hardware_acceptance=0')
