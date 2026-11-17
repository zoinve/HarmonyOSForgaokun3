"""Inspect original read-only USB dump and native JSON dependencies offline."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent


if __name__ == '__main__':
    read = runpy.run_path(str(BASE / 'audit-board-driver-contracts-126.py'))['read']
    resolve = runpy.run_path(str(BASE / 'audit-usb-implementation-150.py'))['resolve']
    report = ROOT / 'reports/usb-public-dump-154'
    assert not report.exists()
    report.mkdir()
    libraries = []
    for index, requested in enumerate(['/system/lib64/libusbservice.z.so', '/system/lib64/libcjson.so.1',
        '/system/lib64/libupdatecjson.z.so', '/system/bin/hidumper']):
        target, data, links = resolve(read, requested)
        row = dict(requested=requested, resolved=target, links=links, elf_resolved=bool(data))
        if data:
            binary = report / (str(index) + '-' + target.rsplit('/', 1)[1])
            binary.open('xb').write(data)
            dynamic = subprocess.check_output(['readelf', '-dW', str(binary)], text=True)
            symbols = subprocess.check_output(['readelf', '--dyn-syms', '--wide', str(binary)], text=True)
            strings = subprocess.run(['strings', '-a'], input=data, capture_output=True, check=True).stdout.decode(errors='replace').splitlines()
            row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), dynamic=dynamic,
                glibc_dependency_present='libc.so.6' in dynamic,
                relevant_symbols=[line for line in symbols.splitlines() if re.search(r'cJSON_|Dump|GetDevices|GetDeviceList|execv', line)][:120],
                selected_strings=[line for line in strings if re.search(r'usb_host -a|Usb Host all device|usb host list info|dump help|Refer to|serialNumber|busNum|devAddress|deviceAddress|vendorId|productId|manufacturerName|devices_|deviceList|configuration', line)][:150])
        libraries.append(row)
    result = dict(libraries=libraries, source_images_opened_read_only=True, binaries_executed=False,
        binaries_patched=False, target_state_modified=False, dump_may_contain_serials_must_sanitize_before_export=True)
    (report / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(libraries=[dict(path=row['resolved'], elf=row['elf_resolved'],
        glibc=row.get('glibc_dependency_present'), selected_strings=row.get('selected_strings')) for row in libraries]), indent=2))
