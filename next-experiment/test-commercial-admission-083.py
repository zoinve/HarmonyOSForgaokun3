"""Admit original service preservation and only credential-free real scanning."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
parse = runpy.run_path(str(Path(__file__).with_name('audit-commercial-network-inputs-079.py')))['members']


def main():
    old, new = [{n: (m, b) for n, m, b in parse(gzip.decompress((BUILD / f'commercial61-native-{number}/initrd.img').read_bytes()))} for number in ('082', '083')]
    assert set(old) <= set(new)
    assert {n for n in old if old[n] != new[n]} == {'init'}
    assert set(new) - set(old) == {'network083-control', 'native-target/network083', 'native-target/network083/wpa.conf'}
    assert new['native-target/network083/wpa.conf'][1] == b'ctrl_interface=DIR=/data/local/tmp/wpa_ctrl GROUP=1010\nupdate_config=0\nap_scan=1\n'
    record = json.loads((ROOT / 'reports/commercial61-native-083/supplicant-provenance.json').read_text())
    assert hashlib.sha256(new['network083-control'][1]).hexdigest() == record['helper_sha256']
    helper = (ROOT / 'next-experiment/network-supplicant-083.c').read_bytes()
    assert hashlib.sha256(helper).hexdigest() == record['helper_source_sha256']
    source = (BUILD / 'commercial61-native-083/init.c').read_text()
    assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD' in source
    assert source.count('probe("wifi-tools-load083", load083, 12)') == 1
    assert record['sha256'] in source
    assert 'NETWORK083_TOOLS_VERIFIED_AND_EXTRACTED_RAM_ONLY' in source
    assert 'sha256sum' in source and 'tar -xzf' in source
    assert 'i==2 && !moved082' in source and 'i==4 && started083' in source
    assert 'force-stop' not in source
    assert b'const int kinds[] = {CLONE_NEWNET, CLONE_NEWNS, CLONE_NEWPID}' in helper
    assert b'if (stat(path, &after) || !same(&after, &wanted[i])) _exit(72)' in helper
    assert b'"-Dnl80211"' in helper and b'"-iwlan0"' in helper
    assert all(value not in helper for value in (b'"-K"', b'SET_NETWORK', b'ADD_NETWORK', b'SAVE_CONFIG'))
    install = json.loads((ROOT / 'reports/commercial-network-inputs-audit-083/tool-installation.json').read_text())
    assert install['sha256'] == record['sha256'] and install['esp_written'] is False
    assert not install['ubuntu_network_modified'] and not install['credentials_read']
    result = dict(existing_members_init_only=True, exact_new_helper_config_members=True,
                  original_services_bootstrap_firmware_unchanged=True, credential_free_configuration=True,
                  pinned_external_package_not_on_esp=True, original_three_namespaces_preserved=True,
                  target_context_identity_verified=True, no_keys_debug_or_association_commands=True,
                  bounded_load_start_and_observers=True)
    with (ROOT / 'reports/commercial61-native-083/admission-test.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    workflow = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-083.py')))['source083']
    for action in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
        generated = workflow(action)
        compile(generated, '<workflow083>', 'exec')
        if action == 'install-commercial-native':
            assert "'initrd /commercial61-native-082/initrd.img','initrd /commercial61-native-083/initrd.img'" in generated
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
