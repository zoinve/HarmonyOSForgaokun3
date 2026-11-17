"""Resolve original USB public service identity read-only, without dumping device data."""
from pathlib import Path
import hashlib
import json
import runpy
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/usb-dump-contract-162'


def filtered(value):
    if not isinstance(value,dict):
        return None
    allowed = ['name','path','uid','gid','caps','secon','process','libpath','run-on-create','distributed','dump-level']
    return {name:value[name] for name in allowed if name in value}


if __name__ == '__main__':
    assert not REPORT.exists(), 'preserve numbered evidence'
    reader = runpy.run_path(str(BASE / 'audit-board-driver-contracts-126.py'))
    read,names = reader['read'],reader['names']
    image = reader['IMAGES'] / 'p111-system.kr990-ext4-v1.img'
    inventories,records = {},[]
    for directory in ['/system/etc/init','/system/profile','/system/etc/sa_profile','/system/etc/hidumper']:
        selected = [name for name in names(image,directory) if 'usb' in name.lower() or 'hidump' in name.lower()]
        inventories[directory] = selected
        for name in selected:
            path = directory + '/' + name
            data = read(image,'cat ' + path,True)
            if not data:
                continue
            row = dict(path=path,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
            try:
                content = json.loads(data)
                if isinstance(content,dict):
                    row['process'] = content.get('process')
                    row['services'] = [filtered(service) for service in content.get('services',[])]
                    abilities = content.get('systemability',[])
                    if isinstance(abilities,list):
                        row['systemabilities'] = [filtered(ability) for ability in abilities]
                    row['jobs_omitted'] = 'jobs' in content
            except (ValueError,UnicodeError):
                try:
                    document = ET.fromstring(data)
                    row['xml_public_service_fields'] = [dict(tag=item.tag,text=(item.text or '').strip())
                        for item in document.iter() if item.tag in ['name','process','libpath','run-on-create']]
                except ET.ParseError:
                    row['unsupported_format_not_exported'] = True
            records.append(row)
    result = dict(source_image_read_only=True,original_binaries_executed=False,operational_boot_performed=False,
        raw_device_dump_read=False,device_serials_exported=False,inventories=inventories,records=records,
        native_usb_service_acceptance_verified=False)
    REPORT.mkdir()
    (REPORT / 'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
