"""Read-only original service admission and supplicant path inventory."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')


def read(path):
    result = subprocess.run(['debugfs', '-R', 'cat ' + path, str(IMAGE)],
                            capture_output=True, check=True)
    assert result.stdout and b'File not found' not in result.stderr
    return result.stdout


def main():
    folder = ROOT / 'reports/commercial-network-source-audit-082'
    folder.mkdir(exist_ok=False)
    cfg = read('/system/etc/init/wifi_standard.cfg')
    profile = read('/system/profile/zz_l410_wifi_bridge.json')
    config = json.loads(cfg)
    abilities = json.loads(profile)
    service, = [row for row in config['services'] if row['name'] == 'wifi_manager_service']
    assert service['path'] == ['/system/bin/sa_main', '/system/profile/zz_l410_wifi_bridge.json']
    libraries = sorted({row['libpath'] for row in abilities['systemability'] if 'libl410_wifi_compat' in row['libpath']})
    records = []
    for path in libraries:
        binary = read(path)
        name = Path(path).name
        with (folder / name).open('xb') as stream:
            stream.write(binary)
        strings = subprocess.run(['strings', '-a'], input=binary, capture_output=True, check=True).stdout.decode(errors='replace').splitlines()
        selected = [line for line in strings if any(key in line for key in
                    ('wpa_ctrl', 'wpa_supplicant', 'wpa_cli', '/run/', '/sbin/ip',
                     '/system/bin/ip', '/proc/net/route', 'RegisterNetSupplier',
                     'UpdateNetSupplierInfo', 'UpdateNetLinkInfo'))]
        dynamic = subprocess.run(['readelf', '-d', str(folder / name)],
                                 capture_output=True, text=True, check=True).stdout
        records.append(dict(path=path, bytes=len(binary), sha256=hashlib.sha256(binary).hexdigest(),
                            selected_original_strings=selected, dynamic_section=dynamic))
    for name, body in [('wifi_standard.cfg', cfg), ('zz_l410_wifi_bridge.json', profile)]:
        with (folder / name).open('xb') as stream:
            stream.write(body)
    result = dict(original_service=service, original_profile=abilities, libraries=records,
                  original_cfg_sha256=hashlib.sha256(cfg).hexdigest(),
                  original_profile_sha256=hashlib.sha256(profile).hexdigest(),
                  connectivity_internal_declared='ohos.permission.CONNECTIVITY_INTERNAL' in service['permission'],
                  network_admin_declared='CAP_NET_ADMIN' in service['caps'],
                  original_image_written=False, private_binary_executed=False,
                  private_binary_patched=False, commercial_abi_equivalence_assumed=False,
                  real_supplicant_or_network_connectivity_proven=False)
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
