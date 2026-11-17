"""Read original init declarations and parameter ACLs; never run target services."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'reports/commercial-event-declarations-063'
IMAGES = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092')
SOURCES = [('system', 'p111-system.kr990-ext4-v1.img', '/system'),
           ('vendor', 'p109-vendor.kr990-ext4-v1.img', '/vendor'),
           ('sysprod', 'p110-sys_prod.img', ''),
           ('chipprod', 'p108-chip_prod.kr990-ext4-v1.img', '')]


def read(image, command):
    return subprocess.check_output(['debugfs', '-R', command, str(image)],
                                   stderr=subprocess.DEVNULL)


def main():
    assert not OUT.exists(), 'Preserve numbered evidence'
    OUT.mkdir()
    records, events, acl_lines = [], [], []
    for label, filename, root in SOURCES:
        image = IMAGES / filename
        for suffix in ['/etc/init', '/etc/param']:
            directory = root + suffix
            listing = read(image, 'ls -p ' + directory).decode()
            (OUT / (label + suffix.replace('/', '-') + '-listing.txt')).open('x').write(listing)
            for line in listing.splitlines():
                fields = line.split('/')
                if len(fields) < 8 or not fields[2].startswith('100'):
                    continue
                name = fields[5]
                path = directory + '/' + name
                blob = read(image, 'cat ' + path)
                assert len(blob) == int(fields[6]), path
                text = blob.decode(errors='replace')
                matches = [dict(line=i, text=value) for i, value in enumerate(text.splitlines(), 1)
                           if 'bootevent' in value or 'hdf_devmgr' in value or 'composer_host' in value]
                if not matches:
                    continue
                target = label + '-' + name
                (OUT / target).open('xb').write(blob)
                records.append(dict(image=filename, path=path, file=target,
                                    sha256=hashlib.sha256(blob).hexdigest(), matches=matches))
                if name.endswith('.cfg'):
                    config = json.loads(text)
                    for service in config.get('services', []):
                        declared = service.get('bootevents', [])
                        if declared:
                            events.append(dict(image=label, path=path, service=service.get('name'),
                                               uid=service.get('uid'), gid=service.get('gid'),
                                               bootevents=declared))
                elif name.endswith('.dac'):
                    acl_lines.extend(dict(image=label, path=path, **match) for match in matches)
    log = (BASE / 'reports/commercial61-native-063/runtime-evidence/raw/interactive-hilog030.log').read_text(errors='replace')
    writes = [dict(name=m[1], result=int(m[2]), log=m[0]) for m in re.finditer(
        r'[^\n]*SystemSetParameter name (bootevent\.\S+) id:\d+ ret:(\d+)[^\n]*', log)]
    result = dict(original_files=records, declared_service_events=events, original_acl_matches=acl_lines,
                  observed_external_writes=writes, internal_writes_not_fully_observed=True,
                  declarations_not_runtime_registration_proof=True, images_modified=False,
                  boot_flags_written=False, services_executed=False)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(matching_files=len(records), service_declarations=events,
                          acl_matches=acl_lines, external_write_failures=[w for w in writes if w['result']]), indent=2))


if __name__ == '__main__':
    main()
