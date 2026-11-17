"""Validate exact archive delta, firmware provenance and original lifecycle."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import stat

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
parser = runpy.run_path(str(Path(__file__).with_name('audit-commercial-network-inputs-079.py')))['members']


def load(number):
    return {n: (m, b) for n, m, b in parser(gzip.decompress((BUILD / f'commercial61-native-{number}/initrd.img').read_bytes()))}


def main():
    old, new = load('078'), load('079')
    assert not set(old) - set(new)
    changed = {n for n in new if new[n] != old.get(n)}
    core = {'init', 'native-target/samgr_standard005.cfg', 'native-target/commercial-desktop077.sh'}
    assert core <= changed
    firmware = json.loads((BUILD / 'native-wifi-firmware-079/result.json').read_text())
    expected = set(core)
    for row in firmware['firmware']:
        if '/nfa765/' in row['path']:
            continue
        name = 'lib/firmware/' + row['path']
        expected.add(name)
        mode, body = new[name]
        if row['kind'] == 'file':
            assert stat.S_ISREG(mode) and hashlib.sha256(body).hexdigest() == row['sha256']
        else:
            assert stat.S_ISLNK(mode) and body.decode() == row['target']
        for parent in Path(name).parents:
            if str(parent) != '.' and str(parent) not in old:
                expected.add(str(parent))
                assert stat.S_ISDIR(new[str(parent)][0])
    assert changed == expected, (changed - expected, expected - changed)
    config = 'native-target/samgr_standard005.cfg'
    before, after = [json.loads(entries[config][1]) for entries in (old, new)]
    originals_before = [s for s in before['services'] if not s['name'].startswith('matebook_desktop')]
    originals_after = [s for s in after['services'] if not s['name'].startswith('matebook_desktop')]
    assert originals_before == originals_after
    assert dict(before, services=[]) == dict(after, services=[])
    script = new['native-target/commercial-desktop077.sh'][1].decode()
    assert 'force-stop' not in script and 'aa start' not in script
    assert 'device_provisioned' not in script and 'user_setup_complete' not in script
    assert new['native-target/bootstrap'] == old['native-target/bootstrap']
    generated = (BUILD / 'commercial61-native-079/init.c').read_text()
    assert generated.count('"ath11k_pci"') == 1
    assert 'probe("wifi-driver079", wifi079, 15)' in generated
    assert 'probe("wifi-observation079", net079, 8)' in generated
    assert 'wpa_supplicant' not in generated and 'iw scan' not in generated
    result = dict(exact_archive_delta=True, copied_firmware_hashes_verified=True,
                  original_service_definitions_preserved=True, no_oobe_stop_or_finish=True,
                  original_bootstrap_unchanged=True, bounded_module_probe=True,
                  no_network_credentials_or_association=True)
    output = ROOT / 'reports/commercial61-native-079/admission-test.json'
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
    workflow = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-079.py')))
    source = workflow['source079']('install-commercial-native')
    assert "'initrd /commercial61-native-078/initrd.img','initrd /commercial61-native-079/initrd.img'" in source
    compile(source, '<install079>', 'exec')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
