"""Separate declared Settings routes from weak PCSettings runtime observations."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
PC = 'com.huawei.hmos.pcsettings'


def routes(hap):
    module = hap['metadata']['module.json']
    abilities = []
    for ability in module['module'].get('abilities', []):
        menus = [json.loads(item['value']) for item in ability.get('metadata', [])
                 if item.get('name') == 'metadata.settings.menu.v1']
        abilities.append(dict(name=ability['name'], visible=ability.get('visible'),
            exported=ability.get('exported'),
            actions=sorted({action for skill in ability.get('skills', [])
                            for action in skill.get('actions', [])}), menus=menus))
    return dict(bundle=module['app']['bundleName'], main_element=module['module'].get('mainElement'),
        hap_sha256=hap['sha256'], abilities=abilities,
        preceding_bytes_contain_signature_marker=b'<hap sign block>' in bytes.fromhex(hap['preceding_32_bytes_hex']),
        cryptographic_verification_performed=False)


def observations(text):
    lines = text.splitlines()
    return dict(token_restore_lines=[i for i,line in enumerate(lines, 1)
                    if 'Restore hap token ' in line and 'bundle name '+PC+' user 100,' in line],
        special_user_key_miss_lines=[i for i,line in enumerate(lines, 1)
                    if 'key:'+PC+'_-3 not found' in line],
        user100_installation_verified=False, ability_launch_verified=False,
        replacement_for_main_settings_verified=False)


if __name__ == '__main__':
    report = ROOT / 'reports/settings-routing-177'
    assert not report.exists(), 'preserve numbered evidence'
    source = ROOT / 'reports/settings-diagnostics-155/result.json'
    raw = source.read_bytes()
    evidence = ROOT / 'reports/commercial61-native-173/runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, expected in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data) == expected['bytes']
        assert hashlib.sha256(data).hexdigest() == expected['sha256'], name
    result = dict(source_metadata_sha256=hashlib.sha256(raw).hexdigest(),
        run=manifest['run'], verified_native_file_count=len(manifest['files']),
        packages=[routes(hap) for hap in json.loads(raw)['original_haps']],
        pcsettings_runtime=observations((evidence / 'raw/interactive-hilog030.log').read_text(errors='replace')),
        settings_repaired=False, target_modified=False, signature_checks_modified=False)
    report.mkdir()
    (report / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result['pcsettings_runtime'], indent=2))
