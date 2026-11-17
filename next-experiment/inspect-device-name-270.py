from pathlib import Path
import json
import runpy

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    helpers = runpy.run_path(str(BASE / 'inspect-radio-contracts-259.py'))
    read, strings = helpers['read'], helpers['strings']
    image = 'p111-system.kr990-ext4-v1.img'
    paths = ['/system/lib64/libdeviceinfoservice.z.so']
    terms = ['device.name', 'device_name', 'DeviceName', 'product.name', 'settings.general']
    rows = []
    for path in paths:
        lines = strings(read(image, path))
        rows.append(dict(path=path, matching_strings=[line for line in lines
            if any(term in line for term in terms)]))
    result = dict(libraries=rows, original_images_modified=False,
                  binaries_executed=False, persisted_name_changed=False)
    dest = BASE.parent / 'reports/device-name-contract-270.json'
    dest.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
