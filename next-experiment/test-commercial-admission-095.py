"""Validate exact RAM changes and workflow guards; no native boot."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')

if __name__ == '__main__':
    report = ROOT/'reports/commercial61-native-095'
    out = report/'admission-test.json'
    assert not out.exists()
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    def archive(number):
        return {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD/f'commercial61-native-{number}/initrd.img').read_bytes()))}
    before, after = archive('094'), archive('095')
    key = 'native-target/commercial-desktop077.sh'
    expected = before[key][1].replace(b'/system/bin/id\n', b'/system/bin/id\n/system/bin/sh /commercial-normal-close095.sh &\n', 1)
    assert after[key][1] == expected
    assert all(before[n] == after[n] for n in before if n != key)
    assert set(after)-set(before) == {'native-target/native-normal-close095', 'native-target/commercial-normal-close095.sh', 'native-target/commercial-focus095.awk'}
    shell = json.loads((report/'normal-close-shell-tests.json').read_text())
    assert len(shell['scenarios']) == 10
    assert shell['worker_sha256'] == hashlib.sha256(after['native-target/commercial-normal-close095.sh'][1]).hexdigest()
    tests = json.loads((ROOT/'reports/native-normal-close-095-tests-r2.json').read_text())
    assert tests['tests']['aarch64']['binary_sha256'] == hashlib.sha256(after['native-target/native-normal-close095'][1]).hexdigest()
    overlay = json.loads((report/'overlay-result.json').read_text())
    assert overlay['ordered_chain_equals_full_095'] is True
    result = dict(only_declared_ram_diagnostic_changes=True, original_cores_and_helpers_identical=True,
                  original_hardware_identity_and_network_diagnostics_preserved=True,
                  ten_shell_scenarios_pass=True, native_keyboard_sequence_tests_pass=True,
                  twelve_focus_guard_scenarios_pass=True, ordered_chain_verified=True)
    # The generator requires this gate; remove it if any generated source fails validation.
    out.open('x').write(json.dumps(result, indent=2))
    try:
        workflow = runpy.run_path(str(BASE/'commercial-workflow-095.py'))
        sources = {name: workflow['source095'](name) for name in ('install-commercial-native', 'run-commercial-native',
                   'retrieve-commercial-evidence', 'verify-commercial-return')}
        for name, source in sources.items():
            compile(source, name, 'exec')
        install = sources['install-commercial-native']
        assert "assert sha(esp/'commercial61-native-092/early094.img')=='f9055bc63beb3daf5f2cd7c7b4529708a6c0f5d42c003c2bddc3b701199aa85e'" in install
        assert "'initrd /commercial61-native-092/early094.img','initrd /commercial61-native-095/initrd.img',options" in install
        assert "dest=esp/'commercial61-native-095'" in install and "dest/'early094.img'" not in install
        assert '32*1024**2' in install and "assert entry.stat().st_size<cluster" in install
        assert 'physical serial found; refusing export' in sources['retrieve-commercial-evidence']
        assert 'original UDID found; refusing export' in sources['retrieve-commercial-evidence']
        assert json.loads((ROOT/'reports/commercial61-native-094/interrupted-run-audit.json').read_text())['run'] in sources['retrieve-commercial-evidence']
        for name, source in sources.items():
            (report/(name+'.generated.py')).open('x').write(source)
    except BaseException:
        # A failed admission artifact must never be mistaken for an install gate.
        out.rename(report/'admission-test-failed.json')
        raise
    print(json.dumps(result, indent=2))
