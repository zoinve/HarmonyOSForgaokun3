"""Read original input/USB service contracts and uevent permissions offline."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
IMAGES = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092')


if __name__ == '__main__':
    tools = runpy.run_path(str(BASE / 'audit-board-driver-contracts-126.py'))
    read, names = tools['read'], tools['names']
    report = ROOT / 'reports/input-usb-contracts-149'
    assert not report.exists()
    report.mkdir()
    libraries, configs, inventories = [], [], {}
    library_pattern = re.compile(r'^libusb_host_interface|^libusb_shared|^libinput-third-mmi|^libusb\.z|^libusb_service', re.I)
    config_pattern = re.compile(r'usb|multimodalinput|storage|ueventd', re.I)
    for image_name, prefix, target_prefix, label in [
        ('p111-system.kr990-ext4-v1.img', '/system', '/system', 'system'),
        ('p109-vendor.kr990-ext4-v1.img', '', '/vendor', 'vendor')]:
        image = IMAGES / image_name
        for suffix in ['/lib64', '/lib64/chipsetsdk', '/lib64/chipset-sdk', '/etc', '/etc/init', '/etc/ueventd']:
            directory = prefix + suffix
            entries = names(image, directory)
            inventories[label + suffix] = entries
            for name in entries:
                source = directory + '/' + name
                target = target_prefix + suffix + '/' + name
                if suffix.startswith('/lib64') and library_pattern.search(name) and '.so' in name:
                    data = read(image, 'cat ' + source, True)
                    if not data.startswith(b'\x7fELF'):
                        continue
                    binary = report / (label + '-' + suffix.rsplit('/', 1)[1] + '-' + name)
                    binary.open('xb').write(data)
                    symbols = subprocess.check_output(['readelf', '--dyn-syms', '--wide', str(binary)], text=True)
                    dynamic = subprocess.check_output(['readelf', '-d', str(binary)], text=True)
                    strings = subprocess.run(['strings', '-a'], input=data, capture_output=True, check=True).stdout.decode(errors='replace').splitlines()
                    libraries.append(dict(path=target, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), dynamic=dynamic,
                        contract_symbols=[line for line in symbols.splitlines() if re.search(r'UsbHost|libusb_|libinput_|DriverEntry|Hdf', line)][:200],
                        contract_strings=[line for line in strings if re.search(r'/sys/|/dev/|libusb|usbfs|permission|Permission|uevent|LIBINPUT|touchscreen', line)][:180]))
                elif suffix.startswith('/etc') and config_pattern.search(name):
                    data = read(image, 'cat ' + source, True)
                    if not data or len(data) > 262144 or b'\x00' in data:
                        continue
                    try:
                        content = json.loads(data)
                    except (ValueError, UnicodeError):
                        content = dict(format='text', relevant_lines=[line for line in data.decode('utf-8', errors='replace').splitlines()
                            if re.search(r'usb|input|storage|uevent|^\s*#', line, re.I)][:200])
                    configs.append(dict(path=target, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), content=content))
    result = dict(inventories=inventories, libraries=libraries, configs=configs, source_images_opened_read_only=True,
        binaries_executed=False, binaries_patched=False, target_state_modified=False,
        service_access_and_physical_interaction_not_inferred=True)
    (report / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(libraries=[r['path'] for r in libraries], configs=configs), indent=2))
