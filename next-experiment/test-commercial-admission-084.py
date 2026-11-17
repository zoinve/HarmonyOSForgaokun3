"""No credential in initrd; original services and real networking remain intact."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
parse = runpy.run_path(str(Path(__file__).with_name('audit-commercial-network-inputs-079.py')))['members']


def main():
    old, new = [{n: (m, b) for n, m, b in parse(gzip.decompress((BUILD / f'commercial61-native-{number}/initrd.img').read_bytes()))} for number in ('083', '084')]
    assert set(old) <= set(new)
    assert {n for n in old if old[n] != new[n]} == {'init'}
    assert set(new) - set(old) == {'network084-control', 'native-target/network084'}
    assert 'native-target/network084/wpa.conf' not in new
    assert new['native-target/network084'][0] & 0o777 == 0o700
    record = json.loads((ROOT / 'reports/commercial61-native-084/association-provenance.json').read_text())
    assert hashlib.sha256(new['network084-control'][1]).hexdigest() == record['helper_sha256']
    helper = runpy.run_path(str(Path(__file__).with_name('commercial-network-helper-084.py')))['SOURCE']
    assert hashlib.sha256(helper.encode()).hexdigest() == record['helper_source_sha256']
    assert 'const int kinds[] = {CLONE_NEWNET, CLONE_NEWNS, CLONE_NEWPID}' in helper
    assert 'if (stat(path, &after) || !same(&after, &wanted[i])) _exit(72)' in helper
    assert 'getifaddrs(&head)' in helper and 'count<64' in helper and 'bytes<16384' in helper
    assert '-c/network084/wpa.conf' in helper
    assert all(value not in helper for value in ('"-K"', 'SET_NETWORK', 'ADD_NETWORK', 'SAVE_CONFIG', 'route", "add'))
    assert '/data/service/el1/public/dhcp/dhcp_cache.conf' in helper
    source = (BUILD / 'commercial61-native-084/init.c').read_text()
    assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD' in source
    assert source.count('probe("wifi-private-config084",load084,8)') == 1
    assert record['sha256'] in source
    assert 'NETWORK084_PRIVATE_CONFIG_VERIFIED_RAM_ONLY' in source
    assert 'credentials_supplied=1 association_requested=1' in source
    assert '(i==4 || i==7 || i==10 || i==13) && started083' in source
    assert 'network083_command(child,"scan")' not in source
    assert 'force-stop' not in source
    assert not record['credential_exported'] and not record['original_ubuntu_network_modified']
    result = dict(existing_members_init_only=True, exact_helper_private_directory_delta=True,
                  credential_not_packaged_or_exported=True, runtime_private_config_hash_guarded=True,
                  original_services_bootstrap_firmware_unchanged=True,
                  original_namespaces_and_identity_checks_preserved=True,
                  real_original_dhcp_and_netmanager_unchanged=True,
                  read_only_bounded_state_observers=True, no_oobe_stop_or_fake_connection=True)
    with (ROOT / 'reports/commercial61-native-084/admission-test.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    workflow = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-084.py')))['source084']
    for action in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
        generated = workflow(action)
        compile(generated, '<workflow084>', 'exec')
        if action == 'install-commercial-native':
            assert "'initrd /commercial61-native-083/initrd.img','initrd /commercial61-native-084/initrd.img'" in generated
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
