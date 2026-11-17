"""Read the supplied image's HCI host configuration and implementation ABI."""
from pathlib import Path
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
IMAGES = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092')
REPORT = ROOT / 'reports/radio-contracts-259'


def read(image, path):
    proc = subprocess.run(['debugfs', '-R', 'cat ' + path, str(IMAGES / image)],
                          capture_output=True, check=True)
    assert proc.stdout, path
    return proc.stdout


def strings(data):
    return subprocess.run(['strings', '-a'], input=data, capture_output=True,
                          check=True).stdout.decode(errors='replace').splitlines()


if __name__ == '__main__':
    assert not REPORT.exists(), 'preserve numbered evidence'
    config = strings(read('p108-chip_prod.kr990-ext4-v1.img', '/etc/hdfconfig/hdf_default.hcb'))
    contexts = []
    for i, line in enumerate(config):
        if re.search('bluetooth|hci|blue_host', line, re.I):
            contexts.append(dict(index=i, surrounding_strings=config[max(0, i-5):i+6]))
    libraries = []
    for name in ['libhci_interface_service_1.0.z.so', 'libbluetooth_hci_hdi_driver.z.so', 'libbt_vendor.z.so']:
        data = read('p109-vendor.kr990-ext4-v1.img', '/lib64/' + name)
        assert data.startswith(b'\x7fELF'), name
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / name
            binary.write_bytes(data)
            symbols = subprocess.check_output(['readelf', '--dyn-syms', '--wide', str(binary)], text=True)
            dynamic = subprocess.check_output(['readelf', '-d', str(binary)], text=True)
        libraries.append(dict(name=name,
            dependencies=re.findall(r'NEEDED.*\[(.*?)\]', dynamic),
            symbols=[line.strip() for line in symbols.splitlines()
                     if re.search('Hci|HCI|Vendor|vendor|Create|ImplGet|DriverEntry', line)],
            paths_and_contracts=[line for line in strings(data)
                if re.search(r'/dev/|/sys/|\.so|Hci|HCI|[Vv]endor|[Ii]nit.*fail', line)][:100]))
    result = dict(hdf_radio_context=contexts, libraries=libraries,
                  original_images_modified=False, target_modified=False,
                  image_binaries_executed=False, filesystem_validation_suite_rerun=False)
    REPORT.mkdir()
    (REPORT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
