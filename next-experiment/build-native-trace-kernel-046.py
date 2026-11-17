# Independent target trace capability; preserve authentic 045 Binder semantics.
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

BASE = Path(__file__).resolve().parents[1]
ROOT = Path('/home/zoinve/harmony-virgl-883')
OLD = ROOT / 'native-binder-kernel-045'
WORK = ROOT / 'native-trace-kernel-046'
OUT = BASE / 'reports/native-trace-kernel-046'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def config(path):
    values = {}
    for line in path.read_text().splitlines():
        if line.startswith('CONFIG_') and '=' in line:
            key, value = line.split('=', 1)
            values[key] = value
    return values


def main():
    assert not WORK.exists() and not OUT.exists(), 'Never overwrite numbered builds'
    assert shutil.disk_usage(ROOT).free > 12 * 1024**3
    before = {name: sha(OLD / 'linux' / name) for name in
              ['drivers/android/binder.c', 'drivers/android/binder_internal.h']}
    old_config_sha = sha(OLD / 'out/.config')
    old_config = config(OLD / 'out/.config')
    WORK.mkdir()
    OUT.mkdir()
    env = dict(os.environ, ARCH='arm64', CROSS_COMPILE='aarch64-linux-gnu-')

    def run(args, label, timeout=1200):
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
    run([str(WORK / 'linux/scripts/config'), '--file', str(WORK / 'out/.config'),
         '-e', 'FTRACE', '-e', 'UPROBE_EVENTS', '-d', 'FUNCTION_TRACER',
         '-d', 'FUNCTION_GRAPH_TRACER', '-d', 'FTRACE_STARTUP_TEST',
         '-d', 'BPF_KPROBE_OVERRIDE'], 'configure.log')
    make = ['make', '-C', str(WORK / 'linux'), 'O=' + str(WORK / 'out')]
    run(make + ['olddefconfig'], 'olddefconfig.log')
    current = config(WORK / 'out/.config')
    for key in ['CONFIG_FTRACE', 'CONFIG_UPROBES', 'CONFIG_UPROBE_EVENTS', 'CONFIG_TRACING']:
        assert current.get(key) == 'y', key
    changes = {key: [old_config.get(key, 'n'), current.get(key, 'n')]
               for key in sorted(set(old_config) | set(current))
               if old_config.get(key, 'n') != current.get(key, 'n')}
    protected = ['SECURITY', 'SELINUX', 'BINDER', 'ACCESS_TOKEN', 'SECCOMP', 'NAMESPACES', 'LSM']
    assert not [key for key in changes if any(part in key for part in protected)], changes
    with (OUT / 'config-changes.json').open('x') as stream:
        json.dump(changes, stream, indent=2)
    shutil.copyfile(WORK / 'out/.config', OUT / 'config')
    run(make + ['-j4', 'Image'], 'build.log', 7200)
    assert sha(OLD / 'out/.config') == old_config_sha
    for name, digest in before.items():
        assert sha(OLD / 'linux' / name) == digest
        assert sha(WORK / 'linux' / name) == digest
    image = WORK / 'out/arch/arm64/boot/Image'
    result = dict(image=str(image), sha256=sha(image), bytes=image.stat().st_size,
                  config_sha256=sha(WORK / 'out/.config'), old_config_sha256=old_config_sha,
                  source_sha256=before, config_changes=changes,
                  release=(WORK / 'out/include/config/kernel.release').read_text().strip(),
                  source_unchanged=True, old_source_config_unchanged=True,
                  target_only_trace_capability=True, security_config_unchanged=True,
                  installed=False, runtime_verified=False, actual_desktop_verified=False)
    with (OUT / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
