"""Archive original link metadata and init loader code without executing either."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess

B = Path(__file__).resolve().parents[1]
OUT = B / 'reports/commercial-root-layout-audit-065'
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')


def main():
    assert not OUT.exists(), 'Preserve numbered evidence'
    OUT.mkdir()
    metadata = subprocess.check_output(['debugfs', '-R', 'stat /chipset', str(IMAGE)], stderr=subprocess.DEVNULL)
    assert b'Type: symlink' in metadata and b'Fast link dest: "/vendor"' in metadata
    (OUT / 'original-chipset-stat.txt').open('xb').write(metadata)
    binary = B / 'reports/commercial-init-bootgate-audit-063/original-init'
    blob = binary.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == '130f2d9d461379055e1be65908b69ac2db482c54d181f022cced588fef97f9e7'
    assert blob[0xc082:].split(b'\0', 1)[0] == b'const.cust.config_dir_layer'
    assert blob[0x10397:].split(b'\0', 1)[0] == b'/system:/chipset:/sys_prod:/chip_prod'
    for name, start, end in [('default-parameter-loading.asm', 0x34bc4, 0x34c64),
                             ('GetCfgDirList.asm', 0x70d44, 0x70e7c)]:
        assembly = subprocess.check_output(['llvm-objdump-19', '-d', '--start-address=' + hex(start),
                                           '--stop-address=' + hex(end), str(binary)])
        (OUT / name).open('xb').write(assembly)
    before = runpy.run_path(str(B / 'next-experiment/build-commercial-native-064.py'))['inner']
    module = runpy.run_path(str(B / 'next-experiment/commercial-root-layout-065.py'))
    after = module['repair'](before)
    assert after.replace(module['FIX'] + '\n', '', 1).replace(module['CALL'], '', 1) == before
    result = dict(original_system_image=str(IMAGE), original_alias='/chipset', original_target='/vendor',
                  init_sha256=hashlib.sha256(blob).hexdigest(),
                  config_dir_parameter='const.cust.config_dir_layer',
                  original_default_directories='/system:/chipset:/sys_prod:/chip_prod',
                  bootstrap_exact_addition_verified=True, original_images_modified=False,
                  original_service_identity_modified=False, original_acl_rules_modified=False,
                  boot_parameters_written=False, runtime_fix_verified=False, desktop_verified=False)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
