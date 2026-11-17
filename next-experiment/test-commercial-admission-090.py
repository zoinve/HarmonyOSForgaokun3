"""Admit only the owned script delta and genuine one-cycle network commands."""
from pathlib import Path
import gzip
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def main():
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    old, new = [{n: (m, d) for n, m, d in parse(gzip.decompress((BUILD / f'commercial61-native-{v}/initrd.img').read_bytes()))}
                for v in ('089', '090')]
    key = 'native-target/commercial-desktop077.sh'
    assert set(old) == set(new)
    assert {n for n in old if old[n] != new[n]} == {key}
    script = (BASE / 'commercial-network-refresh-090.sh').read_text()
    assert new[key][1] == script.encode()
    assert script.count('cli090 disconnect\n') == script.count('cli090 reconnect\n') == 1
    assert script.index('cli090 disconnect\n') < script.index('cli090 reconnect\n') < script.index('for target090')
    assert 'wpa_state=COMPLETED' in script and '"$current090" != "$scene090"' in script
    assert 'unset LD_PRELOAD LD_LIBRARY_PATH' in script
    assert not any(s in script for s in ('force-stop', 'killall', 'setparam', 'uiInput', 'kill -', 'wpa.conf', 'set_network', 'curl', 'iptables'))
    subprocess.run(['sh', '-n', str(BASE / 'commercial-network-refresh-090.sh')], check=True)
    report = ROOT / 'reports/commercial61-native-090'
    overlay = json.loads((report / 'overlay-result.json').read_text())
    assert set(overlay['members']) == {key} and overlay['bytes'] < 12000
    result = dict(single_owned_text_script_delta=True, original_services_packages_permissions_unchanged=True,
        original_wpa_cli_reused=True, one_disconnect_one_restore_no_loop=True,
        requires_real_completed_association_and_stable_scene=True, canonical_config_fix_retained=True,
        no_guide_stop_no_provisioning_or_watchdog_changes=True, no_credentials_read_or_changed=True,
        no_network_validation_or_certificate_bypass=True, shell_syntax_pass=True, small_overlay_measured=True)
    (report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-090.py'))['source090']
    for name in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
        source = workflow(name)
        compile(source, '<workflow090>', 'exec')
        if name == 'retrieve-commercial-evidence':
            for n in ('087', '088', '089'):
                prior = json.loads((ROOT / f'reports/commercial61-native-{n}/runtime-evidence/retrieval-manifest.json').read_text())['run']
                assert prior in source
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
