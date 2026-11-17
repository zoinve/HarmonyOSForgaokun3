"""Prove diagnostic-only delta and unchanged original service/security inputs."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
parse = runpy.run_path(str(Path(__file__).with_name('audit-commercial-network-inputs-079.py')))['members']


def main():
    old, new = [{n: (m, data) for n, m, data in parse(gzip.decompress((BUILD / f'commercial61-native-{number}/initrd.img').read_bytes()))} for number in ('085', '086')]
    assert set(old) <= set(new)
    assert {n for n in old if old[n] != new[n]} == {'init', 'native-target/commercial-desktop077.sh'}
    assert set(new) - set(old) == {'network086-control'}
    assert 'native-target/network084/wpa.conf' not in new
    assert new['native-target/network084'][0] & 0o777 == 0o700
    folder = ROOT / 'reports/commercial61-native-086'
    record = json.loads((folder / 'association-provenance.json').read_text())
    helper = runpy.run_path(str(Path(__file__).with_name('commercial-network-helper-086.py')))
    assert hashlib.sha256(new['network086-control'][1]).hexdigest() == record['helper_sha256']
    assert hashlib.sha256(helper['SOURCE'].encode()).hexdigest() == record['helper_source_sha256']
    assert (folder / 'bootstrap.c').read_bytes() == (ROOT / 'reports/commercial61-native-085/bootstrap.c').read_bytes()
    assert old['native-target/samgr_standard005.cfg'] == new['native-target/samgr_standard005.cfg']
    assert 'const int kinds[] = {CLONE_NEWNET, CLONE_NEWNS, CLONE_NEWPID}' in helper['SOURCE']
    assert 'if (stat(path, &after) || !same(&after, &wanted[i])) _exit(72)' in helper['SOURCE']
    assert all(value not in helper['SOURCE'] for value in ('"-K"', '--insecure', '--resolve', 'SET_NETWORK', 'ADD_NETWORK', 'SAVE_CONFIG'))
    script = (ROOT / 'next-experiment/commercial-layout-086.sh').read_bytes()
    assert script == new['native-target/commercial-desktop077.sh'][1]
    assert b'for target086 in 100 130' in script
    assert b'/system/bin/timeout 8 /system/bin/uitest dumpLayout -p ' in script
    assert b'force-stop' not in script and b'uiInput' not in script
    source = (BUILD / 'commercial61-native-086/init.c').read_text()
    assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD' in source
    assert source.count('probe("wifi-private-config084",load084,8)') == 1
    assert record['sha256'] in source
    assert 'if(i==10 || i==13)(void)network083_command(child,"events")' in source
    assert '"/network086-control", pid,' in source
    assert '"native-layout086-100.json","native-layout086-130.json"' in source
    assert 'i075<sizeof(names075)/sizeof(names075[0])' in source
    assert 'force-stop' not in source
    assert not record['credential_exported'] and not record['original_ubuntu_network_modified']
    result = dict(exact_diagnostic_only_member_delta=True, all_old_helpers_preserved=True,
                  credential_not_packaged_or_exported=True, runtime_private_config_hash_guarded=True,
                  original_services_bootstrap_firmware_unchanged=True,
                  diagnostic_init_identity_permissions_config_unchanged=True,
                  original_namespaces_and_identity_checks_preserved=True,
                  real_original_dhcp_and_netmanager_unchanged=True,
                  original_uitest_timeout_no_injected_input=True,
                  read_only_bounded_event_reader=True, no_oobe_stop_or_fake_completion=True)
    with (folder / 'admission-test.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    workflow = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-086.py')))['source086']
    for action in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
        generated = workflow(action)
        compile(generated, '<workflow086>', 'exec')
        if action == 'install-commercial-native':
            assert "'initrd /commercial61-native-085/initrd.img','initrd /commercial61-native-086/initrd.img'" in generated
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
