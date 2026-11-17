"""Verify init-only delta and bounded read-only evidence collection."""
from pathlib import Path
import gzip
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
parse = runpy.run_path(str(Path(__file__).with_name('audit-commercial-network-inputs-079.py')))['members']


def main():
    old, new = [{n: (m, b) for n, m, b in parse(gzip.decompress((BUILD / f'commercial61-native-{number}/initrd.img').read_bytes()))} for number in ('080', '081')]
    assert set(old) == set(new)
    assert {n for n in old if old[n] != new[n]} == {'init'}
    source = (BUILD / 'commercial61-native-081/init.c').read_text()
    phases = ['probe("wifi-power081", power080, 8)', 'probe("wifi-pci-power081", pci080, 8)',
              'probe("wifi-qrtr081", qrtr081, 8)', 'probe("wifi-driver081", wifi080, 15)',
              'probe("wifi-observation081", net080, 15)']
    offsets = [source.index(phase) for phase in phases]
    assert offsets == sorted(offsets)
    assert 'qrtr-mhi.ko' in '\n'.join(old)
    assert 'open("/dev/kmsg", O_RDONLY | O_NONBLOCK | O_CLOEXEC)' in source
    assert 'while (records < 512 && bytes < 131072)' in source
    assert 'errno == EPIPE && ++losses <= 4' in source
    assert source.count('network081_kmsg();') == 2
    assert source.count('network081_netifs();') == 2
    assert 'count < 32' in source
    assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD' in source
    assert 'force-stop' not in source and 'wpa_supplicant' not in source
    result = dict(exact_init_only_delta=True, unchanged_services_firmware_bootstrap=True,
                  original_qrtr_transport_packaged=True, ordered_bounded_modules=True,
                  nonblocking_readonly_kmsg=True, bounded_late_evidence=True,
                  original_network_namespace_preserved=True, no_oobe_stop_or_association=True)
    with (ROOT / 'reports/commercial61-native-081/admission-test.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    source = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-081.py')))['source081']('install-commercial-native')
    assert "'initrd /commercial61-native-080/initrd.img','initrd /commercial61-native-081/initrd.img'" in source
    compile(source, '<install081>', 'exec')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
