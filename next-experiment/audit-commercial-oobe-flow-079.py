"""Read-only audit of the original Guide metadata, configs and ABC strings."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

B = Path(__file__).resolve().parents[1]
SOURCE = B / 'reports/commercial-ui-resources-audit-068/HwStartupGuide.hap'
EXPECTED = '392566ac1deefe9a269db3ebe45513038ed773f210e628f0ca55ce73ed34a1a7'
OUT = B / 'reports/commercial-oobe-flow-audit-079'

if __name__ == '__main__':
    blob = SOURCE.read_bytes()
    assert len(blob) == 8838069 and hashlib.sha256(blob).hexdigest() == EXPECTED
    OUT.mkdir(exist_ok=False)
    with zipfile.ZipFile(SOURCE) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        module = json.loads(archive.read('module.json'))
        selected = [n for n in names if n.endswith('.json') and any(
            word in n.lower() for word in ['page_config', 'page_order', 'page_layout', '/profile/', 'skip'])]
        configs = {}
        for index, name in enumerate(selected):
            data = archive.read(name)
            value = json.loads(data)
            configs[name] = value
            (OUT / ('config-%02d.json' % index)).open('x').write(json.dumps(value, indent=2, ensure_ascii=True))
        code = archive.read('ets/modules.abc')
        pattern = re.compile(r'skip|terminate|exit|finish|provision|activat|oobe|QuickSetup|Experience', re.I)
        strings = [dict(offset=m.start(), text=m.group().decode('ascii')) for m in re.finditer(rb'[ -~]{5,}', code)
                   if pattern.search(m.group().decode('ascii'))]
        (OUT / 'original-guide-strings.json').open('x').write(json.dumps(strings, indent=2))
        (OUT / 'module.json').open('x').write(json.dumps(module, indent=2))
        result = dict(source=str(SOURCE.relative_to(B)), source_sha256=EXPECTED,
            original_image_written=False, operational_boot_performed=False,
            original_hap_modified=False, authentication_checks_modified=False,
            abc_sha256=hashlib.sha256(code).hexdigest(),
            abilities=module.get('module', {}).get('abilities', []),
            extension_abilities=module.get('module', {}).get('extensionAbilities', []),
            json_members=selected, rawfile_members=[n for n in names if n.startswith('resources/rawfile/')],
            string_matches=len(strings), strings_do_not_prove_reachability=True)
        (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
        print(json.dumps(dict(result, configs=configs), indent=2))
