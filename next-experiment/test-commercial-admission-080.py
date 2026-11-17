"""Exact delta and real bounded hardware observation admission, no boot."""
from pathlib import Path
import gzip
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
parse = runpy.run_path(str(Path(__file__).with_name('audit-commercial-network-inputs-079.py')))['members']


def main():
    old, new = [{n: (m, b) for n, m, b in parse(gzip.decompress((BUILD / f'commercial61-native-{number}/initrd.img').read_bytes()))} for number in ('079', '080')]
    assert set(old) == set(new)
    assert {n for n in old if old[n] != new[n]} == {'init'}
    source = (BUILD / 'commercial61-native-080/init.c').read_text()
    power = source.index('probe("wifi-power080", power080, 8)')
    pci = source.index('probe("wifi-pci-power080", pci080, 8)')
    driver = source.index('probe("wifi-driver080", wifi080, 15)')
    observation = source.index('probe("wifi-observation080", net080, 15)')
    target = source.index('native_original();', observation)
    assert power < pci < driver < observation < target
    assert 'while [ $i -lt 40 ]' in source and '/bin/busybox sleep 0.25' in source
    assert 'NETWORK080_DEVICE=' in source and 'waiting_for_supplier' in source
    assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD' in source
    assert 'force-stop' not in source and 'wpa_supplicant' not in source
    assert 'pci-pwrctrl-pwrseq.ko' in '\n'.join(old)
    assert 'pwrseq-qcom-wcn.ko' in '\n'.join(old)
    result = dict(exact_init_only_delta=True, unchanged_services_firmware_bootstrap=True,
                  power_dependencies_packaged=True, ordered_original_module_load=True,
                  bounded_phy_window=True, real_pci_supplier_observation=True,
                  original_network_namespace_preserved=True, no_oobe_stop_or_association=True)
    report = ROOT / 'reports/commercial61-native-080/admission-test.json'
    with report.open('x') as stream:
        json.dump(result, stream, indent=2)
    source = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-080.py')))['source080']('install-commercial-native')
    assert "'initrd /commercial61-native-079/initrd.img','initrd /commercial61-native-080/initrd.img'" in source
    compile(source, '<install080>', 'exec')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
