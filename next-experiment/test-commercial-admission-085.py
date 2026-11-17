"""Require exact observation-only archive delta before any device installation."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
parse = runpy.run_path(str(Path(__file__).with_name('audit-commercial-network-inputs-079.py')))['members']


def main():
    old, new = [{n: (m, data) for n, m, data in parse(gzip.decompress((BUILD / f'commercial61-native-{number}/initrd.img').read_bytes()))} for number in ('084', '085')]
    assert set(old) <= set(new)
    assert {n for n in old if old[n] != new[n]} == {'init'}
    assert set(new) - set(old) == {'network085-control'}
    assert 'native-target/network084/wpa.conf' not in new
    assert new['native-target/network084'][0] & 0o777 == 0o700
    folder = ROOT / 'reports/commercial61-native-085'
    record = json.loads((folder / 'association-provenance.json').read_text())
    helper = runpy.run_path(str(Path(__file__).with_name('commercial-network-helper-085.py')))['SOURCE']
    assert hashlib.sha256(new['network085-control'][1]).hexdigest() == record['helper_sha256']
    assert hashlib.sha256(helper.encode()).hexdigest() == record['helper_source_sha256']
    assert (folder / 'bootstrap.c').read_bytes() == (ROOT / 'reports/commercial61-native-084/bootstrap.c').read_bytes()
    assert 'const int kinds[] = {CLONE_NEWNET, CLONE_NEWNS, CLONE_NEWPID}' in helper
    assert 'if (stat(path, &after) || !same(&after, &wanted[i])) _exit(72)' in helper
    assert '-c/network084/wpa.conf' in helper
    assert all(value not in helper for value in ('"-K"', '--insecure', '--resolve', 'SET_NETWORK', 'ADD_NETWORK', 'SAVE_CONFIG'))
    source = (BUILD / 'commercial61-native-085/init.c').read_text()
    assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD' in source
    assert source.count('probe("wifi-private-config084",load084,8)') == 1
    assert record['sha256'] in source
    assert source.count('network083_command(child,"http")') == 1
    assert source.count('network083_command(child,"https")') == 1
    assert 'if(i==7 || i==13)(void)network083_command(child,"freeze")' in source
    assert '"/network085-control", pid,' in source
    assert 'force-stop' not in source
    assert not record['credential_exported'] and not record['original_ubuntu_network_modified']
    result = dict(existing_members_init_only=True, exact_one_helper_delta=True,
                  credential_not_packaged_or_exported=True, runtime_private_config_hash_guarded=True,
                  original_services_bootstrap_firmware_unchanged=True,
                  original_namespaces_and_identity_checks_preserved=True,
                  real_original_dhcp_and_netmanager_unchanged=True,
                  fixed_bounded_original_curl_with_tls_verification=True,
                  read_only_bounded_freeze_reader=True, no_oobe_stop_or_fake_connection=True)
    with (folder / 'admission-test.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    workflow = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-085.py')))['source085']
    for action in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
        generated = workflow(action)
        compile(generated, '<workflow085>', 'exec')
        if action == 'install-commercial-native':
            assert "'initrd /commercial61-native-084/initrd.img','initrd /commercial61-native-085/initrd.img'" in generated
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
