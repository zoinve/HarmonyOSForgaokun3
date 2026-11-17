"""Follow original image library links to the real USB implementation ELF."""
from pathlib import Path
import hashlib
import json
import posixpath
import re
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
IMAGES = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092')


def resolve(read, target):
    links = []
    for _ in range(12):
        if target.startswith('/vendor/'):
            image, source = IMAGES / 'p109-vendor.kr990-ext4-v1.img', target.removeprefix('/vendor')
        elif target.startswith('/system/'):
            image, source = IMAGES / 'p111-system.kr990-ext4-v1.img', target
        else:
            raise ValueError('library link escaped system/vendor: ' + target)
        metadata = read(image, 'stat ' + source, True)
        fast = re.search(rb'^Fast link dest: "([^"\r\n]+)"$', metadata, re.M)
        data = fast[1] if fast else read(image, 'cat ' + source, True)
        if data.startswith(b'\x7fELF'):
            return target, data, links
        if not data:
            return target, b'', links
        link = data.decode('ascii')
        assert len(link) < 512 and re.fullmatch(r'[a-zA-Z0-9_./+-]+', link), (target, 'unexpected link contents')
        new = posixpath.normpath(link if link.startswith('/') else posixpath.join(posixpath.dirname(target), link))
        assert new != target and not any(row['source'] == new for row in links), 'symlink cycle'
        links.append(dict(source=target, link=link, target=new))
        target = new
    raise ValueError('library link depth exceeded')


def collect(read, report_name):
    report = ROOT / 'reports' / report_name
    assert not report.exists()
    report.mkdir()
    result = []
    for index, original in enumerate(['/vendor/lib64/chipsetsdk/libusb_host_interface_service_2.0.z.so',
        '/vendor/lib64/chipsetsdk/libusb_adapter.z.so', '/system/lib64/chipset-sdk/libusb_shared.z.so']):
        target, data, links = resolve(read, original)
        row = dict(requested=original, resolved=target, links=links, elf_present=bool(data),
                   resolution_status='resolved_elf' if data else 'unresolved_not_proven_absent')
        if data:
            binary = report / (str(index) + '-' + target.rsplit('/', 1)[1])
            binary.open('xb').write(data)
            symbols = subprocess.check_output(['readelf', '--dyn-syms', '--wide', str(binary)], text=True)
            strings = subprocess.run(['strings', '-a'], input=data, capture_output=True, check=True).stdout.decode(errors='replace').splitlines()
            row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                dynamic=subprocess.check_output(['readelf', '-d', str(binary)], text=True),
                contract_symbols=[line for line in symbols.splitlines() if re.search(r'UsbHost|libusb|usb_|ioctl|open|read|write|Hdf', line)][:180],
                contract_strings=[line for line in strings if re.search(r'/dev/|/sys/|usbfs|libusb|UsbHostInterfaceImpl|permission|Permission|udev|udevd|uevent|not supported|Not support', line)][:200])
        result.append(row)
    (report / 'result.json').open('x').write(json.dumps(dict(libraries=result, images_opened_read_only=True,
        binaries_executed=False, binaries_patched=False, target_state_modified=False), indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    read = runpy.run_path(str(BASE / 'audit-board-driver-contracts-126.py'))['read']
    collect(read, 'usb-implementation-150')
