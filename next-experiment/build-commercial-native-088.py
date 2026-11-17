"""Reuse fixed core 087; alter only product config and own bounded observation."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import shutil

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def main():
    work = BUILD / 'commercial61-native-088'
    report = ROOT / 'reports/commercial61-native-088'
    assert not work.exists() and not report.exists()
    previous = json.loads((ROOT / 'reports/commercial61-native-087/result.json').read_text())
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    before = {name: (mode, body) for name, mode, body in parse(gzip.decompress((BUILD / 'commercial61-native-087/initrd.img').read_bytes()))}
    result = dict(before)
    key = 'native-target/appdata-sandbox019.json'
    original = json.loads(before[key][1])
    updated = runpy.run_path(str(BASE / 'commercial-config-sandbox-088.py'))['repair'](original)
    result[key] = (before[key][0], (json.dumps(updated, indent=2) + '\n').encode())
    script = (BASE / 'commercial-layout-088.sh').read_bytes()
    key_script = 'native-target/commercial-desktop077.sh'
    result[key_script] = (before[key_script][0], script)
    assert {name for name in before if before[name] != result[name]} == {key, key_script}
    work.mkdir()
    report.mkdir()
    for item in previous['artifacts']:
        if item['name'] == 'initrd.img':
            continue
        source = BUILD / 'commercial61-native-087' / item['name']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item['sha256']
        shutil.copyfile(source, work / item['name'])
    raw = b''.join(pack(name, mode, body, index+1) for index, (name, (mode, body)) in enumerate(result.items()))
    raw += pack('TRAILER!!!', 0, b'', len(result)+1)
    (work / 'initrd.img').open('xb').write(gzip.compress(raw, compresslevel=6, mtime=0))
    (report / 'original-appdata-sandbox.json').open('xb').write(before[key][1])
    (report / 'canonical-appdata-sandbox.json').open('xb').write(result[key][1])
    (report / 'layout-diagnostic088.sh').open('xb').write(script)
    shutil.copyfile(ROOT / 'reports/commercial61-native-087/workspace.json', report / 'workspace.json')
    inherited = json.loads((ROOT / 'reports/commercial61-native-087/workspace-provenance.json').read_text())
    provenance = dict(inherited_core='087', inherited_runtime_run_prefix='commercial61-native-087-',
                      changed_archive_members=sorted([key, key_script]),
                      original_config_sha256=hashlib.sha256(before[key][1]).hexdigest(),
                      updated_config_sha256=hashlib.sha256(result[key][1]).hexdigest(),
                      runtime_bootstrap_sha256=inherited['runtime_bootstrap_sha256'],
                      runtime_bootstrap_source=inherited['runtime_bootstrap_source'],
                      workspace_sha256=inherited['workspace_sha256'],
                      original_images_modified=False, original_hap_modified=False,
                      permissions_identity_or_credentials_modified=False,
                      added_mount_source='/system/etc', added_mount_target='/usr/system/etc',
                      source_already_exposed=True, applies_only_to='com.ohos.sceneboard', runtime_verified=False)
    (report / 'config-provenance.json').open('x').write(json.dumps(provenance, indent=2))
    names = [item['name'] for item in previous['artifacts']]
    previous['artifacts'] = [dict(name=name, bytes=(work/name).stat().st_size,
                                sha256=hashlib.sha256((work/name).read_bytes()).hexdigest()) for name in names]
    previous['inherited_core_identity'] = '087'
    previous['canonical_config_adapter'] = provenance
    previous['runtime_verified'] = False
    for folder in (work, report):
        (folder / 'result.json').open('x').write(json.dumps(previous, indent=2))
    print(json.dumps(provenance, indent=2))


if __name__ == '__main__':
    main()
