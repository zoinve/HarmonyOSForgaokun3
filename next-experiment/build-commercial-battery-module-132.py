"""Build a HarmonyOS-specific real EC module with the original HDI sysfs name."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
RELATIVE = 'drivers/power/supply/huawei-gaokun-battery.c'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def adapt(source):
    old = '.name\t\t\t= "gaokun-ec-battery",'
    assert source.count(old) == 1
    return source.replace(old, '.name\t\t\t= "battery",', 1)


if __name__ == '__main__':
    parent = BUILD / 'native-binder-kernel-045'
    work = BUILD / 'commercial-battery-module-132'
    report = ROOT / 'reports/commercial-battery-module-132'
    assert not work.exists() and not report.exists()
    assert shutil.disk_usage(BUILD).free > 12 * 1024**3
    before = {name: sha(parent / name) for name in ['linux/' + RELATIVE, 'out/.config',
              'out/Module.symvers', 'out/arch/arm64/boot/Image']}
    assert before['out/arch/arm64/boot/Image'] == '925517f23062925ef7a65f088d8ed56a1b73eef5722c02020959373ddacc4e52'
    work.mkdir()
    report.mkdir()
    env = dict(os.environ, ARCH='arm64', CROSS_COMPILE='aarch64-linux-gnu-')
    def run(command, name, timeout=1200):
        with (report / name).open('xb') as stream:
            result = subprocess.run(command, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
        assert result.returncode == 0, (name, result.returncode)
    run(['cp', '-a', '--reflink=auto', str(parent / 'linux'), str(work / 'linux')], 'copy-source.log')
    run(['cp', '-a', '--reflink=auto', str(parent / 'out'), str(work / 'out')], 'copy-build.log')
    makefile = work / 'out/Makefile'
    makefile.write_text(makefile.read_text().replace(str(parent / 'linux'), str(work / 'linux')))
    link = work / 'out/source'
    if link.is_symlink():
        link.unlink()
        link.symlink_to(work / 'linux')
    module = work / 'module'
    module.mkdir()
    original = (parent / 'linux' / RELATIVE).read_text()
    source = module / 'huawei-gaokun-battery.c'
    source.open('x').write(adapt(original))
    (module / 'Makefile').open('x').write('obj-m += huawei-gaokun-battery.o\n')
    run(['make', '-C', str(work / 'linux'), 'O=' + str(work / 'out'),
         'M=' + str(module), '-j4', 'modules'], 'build.log')
    library = module / 'huawei-gaokun-battery.ko'
    modinfo = subprocess.check_output(['modinfo', str(library)], text=True)
    (report / 'modinfo.txt').open('x').write(modinfo)
    assert '7.1.0-rc3-gaokun3-el2 SMP preempt mod_unload aarch64' in modinfo
    assert 'auxiliary:huawei_gaokun_ec.psy' in modinfo
    assert 'huawei-gaokun-ec' in modinfo
    assert all(sha(parent / name) == digest for name, digest in before.items())
    assert sha(work / 'out/.config') == before['out/.config']
    symbols = subprocess.check_output(['aarch64-linux-gnu-nm', str(library)], text=True)
    assert '__ksymtab_' not in symbols
    shutil.copyfile(source, report / source.name)
    result = dict(module=str(library), module_sha256=sha(library), module_bytes=library.stat().st_size,
                  original_source_sha256=before['linux/' + RELATIVE], source_sha256=sha(source),
                  original_kernel_config_and_sources_unchanged=True, kernel_config_sha256=before['out/.config'],
                  original_kernel_sha256=before['out/arch/arm64/boot/Image'],
                  only_power_supply_registration_name_changed=True, actual_ec_access_unchanged=True,
                  charging_controls_and_events_unchanged=True, optional_attributes_not_fabricated=True,
                  sysfs_name='battery', original_battery_hdi_binary_unchanged=True,
                  installed=False, target_runtime_verified=False)
    (report / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
