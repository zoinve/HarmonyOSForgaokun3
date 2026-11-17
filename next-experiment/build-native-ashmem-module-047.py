"""Rebuild the unchanged adapted ashmem source for the trace configuration."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path('/home/zoinve/harmony-virgl-883')
OUT = ROOT / 'native-ashmem-module-047'
REPORT = Path(__file__).resolve().parents[1] / 'reports/native-ashmem-module-047'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OUT.exists() and not REPORT.exists()
    OUT.mkdir()
    REPORT.mkdir()
    old = ROOT / 'native-ashmem-module-001'
    hashes = {name: sha(old / name) for name in ['hmos_ashmem.c', 'ashmem-uapi.h', 'Makefile']}
    for name in hashes:
        shutil.copyfile(old / name, OUT / name)
    args = ['make', '-C', str(ROOT / 'native-trace-kernel-047/out'),
            'ARCH=arm64', 'CROSS_COMPILE=aarch64-linux-gnu-', 'M=' + str(OUT), 'modules']
    result = subprocess.run(args, capture_output=True)
    (REPORT / 'build.stdout').open('xb').write(result.stdout)
    (REPORT / 'build.stderr').open('xb').write(result.stderr)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    assert all(sha(old / name) == digest == sha(OUT / name) for name, digest in hashes.items())
    manifest = dict(module=str(OUT / 'hmos_ashmem.ko'), sha256=sha(OUT / 'hmos_ashmem.ko'),
                    sources=hashes, source_unchanged=True, loaded_in_ubuntu=False)
    (REPORT / 'result.json').open('x').write(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
