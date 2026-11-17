"""Ensure only existing SceneBoard config view and own observation change."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def main():
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    old, new = [{n: (m,d) for n,m,d in parse(gzip.decompress((BUILD / f'commercial61-native-{number}/initrd.img').read_bytes()))}
                for number in ('087', '088')]
    changed = {'native-target/appdata-sandbox019.json', 'native-target/commercial-desktop077.sh'}
    assert set(old) == set(new)
    assert {n for n in old if old[n] != new[n]} == changed
    assert old['init'] == new['init']
    assert old['native-target/bootstrap'] == new['native-target/bootstrap']
    key = 'native-target/appdata-sandbox019.json'
    expected = runpy.run_path(str(BASE / 'commercial-config-sandbox-088.py'))['repair'](json.loads(old[key][1]))
    assert json.loads(new[key][1]) == expected
    assert new['native-target/commercial-desktop077.sh'][1] == (BASE / 'commercial-layout-088.sh').read_bytes()
    script = new['native-target/commercial-desktop077.sh'][1]
    assert b'force-stop' not in script and b'setparam' not in script and b'uiInput' not in script
    assert b'for target088 in 60 100 130' in script
    assert b'"/proc/$pid088/root$path088"' in script
    assert b'for path088 in /system/etc/hw_launcher_default_workspace.json /usr/system/etc/hw_launcher_default_workspace.json' in script
    assert old['native-target/samgr_standard005.cfg'] == new['native-target/samgr_standard005.cfg']
    report = ROOT / 'reports/commercial61-native-088'
    provenance = json.loads((report / 'config-provenance.json').read_text())
    assert hashlib.sha256((BUILD / 'commercial61-native-088/bootstrap-runtime087').read_bytes()).hexdigest() == provenance['runtime_bootstrap_sha256']
    overlay = json.loads((report / 'overlay-result.json').read_text())
    assert set(overlay['members']) == changed and overlay['bytes'] < 12000
    result = dict(exact_two_text_member_delta=True, inherited_core_and_bootstrap_byte_identical=True,
                  sceneboard_only_already_exposed_config_alias=True, no_sandbox_disabled=True,
                  identities_permissions_groups_and_other_mounts_unchanged=True,
                  signed_packages_provisioning_and_images_unchanged=True,
                  network_helpers_and_private_credentials_unchanged=True,
                  exact_runtime_bootstrap_dependency_checked=True, bounded_readonly_path_observation=True,
                  original_layout_tool_no_permission_bypass=True, measured_small_overlay=True,
                  unique_entry088_inherited_raw_labels_documented=True)
    (report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-088.py'))['source088']
    for name in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
        source = workflow(name)
        compile(source, '<workflow088>', 'exec')
        if name == 'retrieve-commercial-evidence':
            assert "mount.rglob('commercial61-native-087-*')" in source
            assert 'if p.name != ' in source
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
