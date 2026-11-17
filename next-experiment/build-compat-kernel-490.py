"""Build an isolated kernel candidate; no install, boot or source-tree copying."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
PARENT = BUILD / 'native-binder-kernel-045'


def config_values(text):
    result = {}
    for line in text.splitlines():
        if line.startswith('CONFIG_') and '=' in line:
            key, value = line.split('=', 1)
            result[key] = value
        elif line.startswith('# CONFIG_') and line.endswith(' is not set'):
            result[line[2:-len(' is not set')]] = 'n'
    return result


def expected_config(original, fragment):
    result = config_values(original)
    changes = config_values(fragment)
    assert changes == dict(CONFIG_MEMCG_V1='y', CONFIG_REBOOT_MODE='y',
        CONFIG_POWER_RESET_QCOM_PON='y', CONFIG_INTERCONNECT_QCOM_OSM_L3='y')
    assert result['CONFIG_MEMCG'] == 'y'
    assert result['CONFIG_ANDROID_BINDER_IPC'] == 'y'
    assert result['CONFIG_INPUT_PM8941_PWRKEY'] == 'y'
    assert result['CONFIG_DRM_MSM'] == 'm'
    assert all(key in result for key in changes)
    result.update(changes)
    return result


if __name__ == '__main__':
    work = BUILD / 'compat-kernel-490'
    report = ROOT / 'reports/compat-kernel-490'
    assert not work.exists() and not report.exists(), 'preserve numbered evidence'
    assert shutil.disk_usage(BUILD).free > 4 * 1024**3
    original = (PARENT / 'out/.config').read_text()
    fragment = (ROOT / 'next-experiment/compat-kernel-489.config').read_text()
    wanted = expected_config(original, fragment)
    work.mkdir()
    report.mkdir()
    env = dict(os.environ, ARCH='arm64', CROSS_COMPILE='aarch64-linux-gnu-')

    def run(args, name, timeout=7200):
        with (report / name).open('xb') as stream:
            result = subprocess.run(args, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
        assert result.returncode == 0, (name, result.returncode)

    run(['cp', '-a', '--reflink=auto', str(PARENT / 'out'), str(work / 'out')], 'copy-output.log')
    # No kernel source modifications are required for these real drivers.
    config = work / 'out/.config'
    config.write_text(original + '\n' + fragment)
    make = ['make', '-C', str(PARENT / 'linux'), 'O=' + str(work / 'out')]
    run(make + ['olddefconfig'], 'olddefconfig.log', 120)
    actual = config_values(config.read_text())
    assert actual == wanted, {key: (wanted.get(key), actual.get(key))
        for key in wanted.keys() | actual.keys() if wanted.get(key) != actual.get(key)}
    delta = {key: dict(before=config_values(original)[key], after=value)
             for key, value in actual.items() if config_values(original).get(key) != value}
    (report / 'config-delta.json').open('x').write(json.dumps(delta, indent=2) + '\n')
    run(make + ['-j4', 'Image', 'modules'], 'build.log')
    assert (PARENT / 'out/.config').read_text() == original
    assert config_values(config.read_text()) == wanted
    image = work / 'out/arch/arm64/boot/Image'
    with image.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    result = dict(image=str(image), bytes=image.stat().st_size, sha256=digest,
        release=(work / 'out/include/config/kernel.release').read_text().strip(),
        config_delta=delta, matching_modules_built=True, original_source_unmodified=True,
        original_kernel_config_unmodified=True, original_binder_token_security_unchanged=True,
        mali_or_hi1103_drivers_imported=False, installed=False, booted=False,
        cgroup_resource_limit_runtime_verified=False, volume_down_physical_event_verified=False,
        huawei_share_file_transfer_verified=False, compatibility_linux_app_verified=False)
    (report / 'result.json').open('x').write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
