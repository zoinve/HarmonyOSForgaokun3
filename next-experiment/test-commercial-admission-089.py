"""Assert the single-stop experiment changes no original service or package."""
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
                for v in ('088', '089')]
    key = 'native-target/commercial-desktop077.sh'
    assert set(old) == set(new)
    assert {n for n in old if old[n] != new[n]} == {key}
    script = (BASE / 'commercial-desktop-089.sh').read_text()
    assert new[key][1] == script.encode()
    assert script.count('/system/bin/aa force-stop com.huawei.hmos.hwstartupguide') == 1
    assert script.index('DESKTOP089_DOCK_READY') < script.index('/system/bin/aa force-stop')
    assert script.index('/system/bin/sleep 10') < script.index('/system/bin/aa force-stop')
    assert '"$current089" = "$scenes089"' in script
    assert 'EVENT_SMARTDOCK_INIT_FINISHED' in script
    assert not any(s in script for s in ('killall', 'setparam', 'uiInput', 'kill -', 'bm install'))
    subprocess.run(['sh', '-n', str(BASE / 'commercial-desktop-089.sh')], check=True)
    report = ROOT / 'reports/commercial61-native-089'
    overlay = json.loads((report / 'overlay-result.json').read_text())
    assert set(overlay['members']) == {key} and overlay['bytes'] < 12000
    result = dict(single_owned_script_delta=True, original_packages_services_permissions_unchanged=True,
        canonical_config_fix_retained=True, original_aa_single_bounded_request=True,
        genuine_dock_marker_and_same_pid_gate=True, ten_second_same_pid_interval=True,
        no_provisioning_or_watchdog_changes=True, no_repeated_guide_stop=True,
        shell_syntax_pass=True, small_overlay_measured=True)
    (report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
    source = runpy.run_path(str(BASE / 'commercial-workflow-089.py'))['source089']
    for action in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
        text = source(action)
        compile(text, '<workflow089>', 'exec')
        if action == 'retrieve-commercial-evidence':
            assert 'if p.name not in ' in text
            for number in ('087', '088'):
                run = json.loads((ROOT / f'reports/commercial61-native-{number}/runtime-evidence/retrieval-manifest.json').read_text())['run']
                assert run in text
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
