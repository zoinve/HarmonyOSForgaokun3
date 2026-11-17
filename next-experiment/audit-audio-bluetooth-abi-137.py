"""Inspect exact image audio/BT contracts without executing or patching binaries."""
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
    report = ROOT / 'reports/audio-bluetooth-abi-137'
    assert not report.exists()
    report.mkdir()
    selected = re.compile(r'audio.*(?:vdi|primary|manager|proxy|service|driver)|bluetooth.*(?:vendor|hci|hdi|interface|driver)|bt_vendor|hdi_bluetooth', re.I)
    libraries, configs, inventories = [], [], {}
    for image_name, prefix, target_prefix, label in [
        ('p111-system.kr990-ext4-v1.img', '/system', '/system', 'system'),
        ('p109-vendor.kr990-ext4-v1.img', '', '/vendor', 'vendor')]:
        image = IMAGES / image_name
        for suffix in ['/lib64', '/lib64/hw', '/lib64/chipset-sdk', '/etc/init', '/etc/audio', '/etc/bluetooth', '/etc/hdfconfig']:
            directory = prefix + suffix
            entries = names(image, directory)
            inventories[label + suffix] = entries
            for name in entries:
                source = directory + '/' + name
                target_path = target_prefix + suffix + '/' + name
                if '/lib64' in suffix and selected.search(name) and '.so' in name:
                    data = read(image, 'cat ' + source, True)
                    if not data.startswith(b'\x7fELF'):
                        continue
                    binary = report / (label + '-' + name)
                    binary.open('xb').write(data)
                    symbols = subprocess.check_output(['readelf', '--dyn-syms', '--wide', str(binary)], text=True)
                    dynamic = subprocess.check_output(['readelf', '-d', str(binary)], text=True)
                    strings = subprocess.run(['strings', '-a'], input=data, capture_output=True, check=True).stdout.decode(errors='replace').splitlines()
                    libraries.append(dict(path=target_path, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), dynamic=dynamic,
                        contract_symbols=[line for line in symbols.splitlines() if re.search(r'GetAudio|Get.*Manager|Vdi|VDI|Vendor|vendor|Hci|HCI|AudioAdapter|AudioRender|AudioCapture|DriverEntry', line)][:300],
                        contract_strings=[line for line in strings if re.search(r'/dev/|/sys/|alsa|pcm_|lib[^ /]+\.so|GetAudioManager|HCI_CHANNEL|BtVendor|bt_vendor|vdi', line, re.I)][:180]))
                elif '/etc/' in suffix and (selected.search(name) or re.search(r'audio|bluetooth|hdf', name, re.I)):
                    data = read(image, 'cat ' + source, True)
                    if not data:
                        continue
                    try:
                        content = json.loads(data)
                    except (ValueError, UnicodeError):
                        strings = subprocess.run(['strings', '-a'], input=data, capture_output=True, check=True).stdout.decode(errors='replace').splitlines()
                        content = dict(format='non_json', selected_strings=[line for line in strings if re.search(r'audio|bluetooth|vendor|hci|primary|host|vdi', line, re.I)][:120])
                    configs.append(dict(path=target_path, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), content=content))
    result = dict(inventories=inventories, libraries=libraries, configs=configs,
                  source_images_opened_read_only=True, binaries_executed=False, binaries_patched=False,
                  target_state_modified=False, abi_compatibility_not_assumed_from_reference=True)
    (report / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(libraries=[row['path'] for row in libraries], configs=[row['path'] for row in configs]), indent=2))
