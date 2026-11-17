"""Check exact candidate changes and every inherited deployment/privacy guard."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


if __name__ == '__main__':
    report = ROOT/'reports/commercial61-native-099'
    output = report/'admission-test.json'
    assert not output.exists()
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    def archive(number):
        return {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD/f'commercial61-native-{number}/initrd.img').read_bytes()))}
    before, after = archive('095'), archive('099')
    key = 'native-target/commercial-desktop077.sh'
    expected = before[key][1].replace(b'/system/bin/sh /commercial-normal-close095.sh &\n',
        b'/system/bin/sh /commercial-reference-observer099.sh &\n', 1).replace(
        b'REFRESH090_BEGIN real_wpa_cycle_once=1 no_guide_stop=1 provisioning_unchanged=1',
        b'REFERENCE099_BEGIN real_wpa_cycle_once=1 reference_stop_once=1 provisioning_unchanged=1', 1)
    assert after[key][1] == expected
    assert all(after[n] == v for n, v in before.items() if n != key)
    assert set(after)-set(before) == {'native-target/harmonymac-reference099.sh',
                                     'native-target/commercial-reference-observer099.sh'}
    builder = runpy.run_path(str(BASE/'build-commercial-native-099.py'))
    original, adapted = builder['reference_script']()
    assert after['native-target/harmonymac-reference099.sh'] == (0o100755, adapted)
    observer = (BASE/'commercial-reference-observer-099.sh').read_bytes()
    assert after['native-target/commercial-reference-observer099.sh'] == (0o100755, observer)
    tests = json.loads((ROOT/'reports/reference-order-099-tests.json').read_text())
    sha = lambda b: hashlib.sha256(b).hexdigest()
    assert tests['reference_sha256'] == sha(original)
    assert tests['adapted_sha256'] == sha(adapted)
    assert tests['observer_sha256'] == sha(observer)
    assert len(tests['scenarios']) == 7 and tests['all_scenarios_passed']
    overlay = json.loads((report/'overlay-result.json').read_text())
    assert overlay['ordered_chain_equals_full_099']
    result = dict(only_declared_ram_script_changes=True, original_cores_identical=True,
                  real_identity_network_and_security_unchanged=True,
                  original_reference_order_and_commands_verified=True,
                  seven_shell_scenarios_pass=True, ordered_chain_verified=True,
                  alt_f4_not_launched=True, one_force_stop_only=True)
    output.open('x').write(json.dumps(result, indent=2))
    try:
        workflow = runpy.run_path(str(BASE/'commercial-workflow-099.py'))
        sources = {n: workflow['source099'](n) for n in ('install-commercial-native', 'run-commercial-native',
                   'retrieve-commercial-evidence', 'verify-commercial-return')}
        for name, source in sources.items():
            compile(source, name, 'exec')
            assert 'commercial61-native-099' in source
            assert 'StrictHostKeyChecking=yes' in source
        install = sources['install-commercial-native']
        parent = json.loads((ROOT/'reports/commercial61-native-095/overlay-result.json').read_text())
        assert "assert sha(esp/'commercial61-native-095/initrd.img')=="+repr(parent['sha256']) in install
        assert "'initrd /commercial61-native-095/initrd.img','initrd /commercial61-native-099/initrd.img',options" in install
        assert "dest=esp/'commercial61-native-099'" in install
        assert '32*1024**2' in install and "assert entry.stat().st_size<cluster" in install
        assert "sha(images/n)==m['sha256']" in install
        retrieve = sources['retrieve-commercial-evidence']
        assert 'physical serial found; refusing export' in retrieve
        assert 'original UDID found; refusing export' in retrieve
        previous = json.loads((ROOT/'reports/commercial61-native-095/runtime-evidence/retrieval-manifest.json').read_text())['run']
        assert previous in retrieve
        run = sources['run-commercial-native']
        assert "'attempt_count'" not in run or 'attempt_count=1' in run
        assert 'attempt_count=1' in run and '660' in run and 'no retries' in run
        assert "'enabled'" in run and "'active'" in run
        verify = sources['verify-commercial-return']
        assert 'commercial_original_images_unchanged=verified' in verify
        assert 'user_authorized_old_entries_removed=removed_entries' in verify
        for name, source in sources.items():
            (report/(name+'.generated.py')).open('x').write(source)
    except BaseException:
        output.rename(report/'admission-test-failed.json')
        raise
    print(json.dumps(result, indent=2))
