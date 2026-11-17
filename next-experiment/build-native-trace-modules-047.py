"""Rebuild matching trace-kernel modules without changing numbered 046."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

BASE = Path(__file__).resolve().parents[1]
ROOT = Path('/home/zoinve/harmony-virgl-883')
OLD = ROOT / 'native-trace-kernel-046'
WORK = ROOT / 'native-trace-kernel-047'
OUT = BASE / 'reports/native-trace-kernel-047'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    assert not WORK.exists() and not OUT.exists(), 'Preserve numbered builds'
    assert shutil.disk_usage(ROOT).free > 12 * 1024**3
    before = {name: sha(OLD / name) for name in
              ['out/.config', 'out/arch/arm64/boot/Image',
               'out/drivers/nvme/host/nvme.ko', 'linux/drivers/android/binder.c']}
    WORK.mkdir()
    OUT.mkdir()
    env = dict(os.environ, ARCH='arm64', CROSS_COMPILE='aarch64-linux-gnu-')

    def run(args, label, timeout=7200):
        with (OUT / label).open('xb') as log:
            result = subprocess.run(args, env=env, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=timeout)
        assert result.returncode == 0, (label, result.returncode)

    for name in ['linux', 'out']:
        run(['cp', '-a', '--reflink=auto', str(OLD / name), str(WORK / name)],
            'copy-' + name + '.log')
    makefile = WORK / 'out/Makefile'
    makefile.write_text(makefile.read_text().replace(str(OLD / 'linux'), str(WORK / 'linux')))
    link = WORK / 'out/source'
    assert link.is_symlink()
    link.unlink()
    link.symlink_to(WORK / 'linux')
    make = ['make', '-C', str(WORK / 'linux'), 'O=' + str(WORK / 'out')]
    run(make + ['-j4', 'Image', 'modules'], 'build.log')
    run(make + ['modules_install', 'INSTALL_MOD_PATH=' + str(WORK / 'modules')],
        'modules-install.log')
    for name, digest in before.items():
        assert sha(OLD / name) == digest
    assert sha(WORK / 'out/.config') == before['out/.config']
    assert sha(WORK / 'linux/drivers/android/binder.c') == before['linux/drivers/android/binder.c']
    modules = list((WORK / 'modules/lib/modules').iterdir())
    assert len(modules) == 1
    module_manifest = {str(p.relative_to(modules[0])): sha(p)
                       for p in modules[0].rglob('*.ko')}
    assert module_manifest
    result = dict(image=str(WORK / 'out/arch/arm64/boot/Image'),
                  image_sha256=sha(WORK / 'out/arch/arm64/boot/Image'),
                  config_sha256=sha(WORK / 'out/.config'),
                  modules_root=str(modules[0]), modules=module_manifest,
                  previous_hashes=before, previous_unchanged=True,
                  configuration_unchanged=True, installed=False,
                  runtime_verified=False, actual_desktop_verified=False)
    with (OUT / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({k: v for k, v in result.items() if k != 'modules'}, indent=2))


if __name__ == '__main__':
    main()
