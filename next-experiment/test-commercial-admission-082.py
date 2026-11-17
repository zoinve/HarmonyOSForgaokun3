"""Admit only the outer init and hash-pinned isolated namespace tools."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import stat

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
parse = runpy.run_path(str(Path(__file__).with_name('audit-commercial-network-inputs-079.py')))['members']


def main():
    old, new = [{n: (m, b) for n, m, b in parse(gzip.decompress((BUILD / f'commercial61-native-{number}/initrd.img').read_bytes()))} for number in ('081', '082')]
    assert set(old) <= set(new)
    assert {n for n in old if old[n] != new[n]} == {'init'}
    provenance = json.loads((ROOT / 'reports/commercial61-native-082/iw-provenance.json').read_text())
    files = {'network082/' + row['path'].lstrip('/'): row['sha256'] for row in provenance['files']}
    files['network082/namespace-observe'] = provenance['helper_sha256']
    added_files = {n for n in set(new) - set(old) if stat.S_ISREG(new[n][0])}
    assert added_files == set(files)
    for name, digest in files.items():
        assert hashlib.sha256(new[name][1]).hexdigest() == digest
    assert all(n == 'network082' or n.startswith('network082/') for n in set(new) - set(old))
    source = (BUILD / 'commercial61-native-082/init.c').read_text()
    assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD' in source
    assert source.count('probe("wifi-namespace-move082", move082, 8)') == 1
    assert source.count('probe("wifi-target-observe082", observe082, 8)') == 1
    assert 'if (!moved082)' in source
    assert '"phy", "phy0", "set", "netns", pid082, NULL' in source
    assert 'force-stop' not in source and 'wpa_supplicant' not in source
    helper = (ROOT / 'next-experiment/network-namespace-observe-082.c').read_bytes()
    assert hashlib.sha256(helper).hexdigest() == provenance['helper_source_sha256']
    assert b'setns(target, CLONE_NEWNET)' in helper
    assert b'after.st_ino != wanted.st_ino' in helper
    result = dict(exact_existing_member_delta_init_only=True, exact_added_tool_hashes=True,
                  isolated_tools_only=True, unchanged_services_firmware_bootstrap=True,
                  original_network_namespace_preserved=True, migration_once_and_bounded=True,
                  namespace_identity_checked=True, no_association_or_oobe_stop=True)
    with (ROOT / 'reports/commercial61-native-082/admission-test.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    workflow = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-082.py')))['source082']
    for action in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
        generated = workflow(action)
        compile(generated, '<workflow082>', 'exec')
        if action == 'install-commercial-native':
            assert "'initrd /commercial61-native-081/initrd.img','initrd /commercial61-native-082/initrd.img'" in generated
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
