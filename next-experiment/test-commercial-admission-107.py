"""Admit only the declared observation delta and inherited operational gates."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import shutil
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def sha(data):
    return hashlib.sha256(data).hexdigest()


if __name__ == '__main__':
    work, report = BUILD / 'commercial61-native-107', ROOT / 'reports/commercial61-native-107'
    output = report / 'admission-test.json'
    assert not output.exists()
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def archive(number):
        return {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD / ('commercial61-native-' + number) / 'initrd.img').read_bytes()))}
    before, after = archive('105'), archive('107')
    changed = {n for n in before if before[n] != after[n]}
    assert changed == {'init', 'early-hardware093.sh', 'native-target/commercial-desktop077.sh'}
    assert set(after) - set(before) == {'native-target/commercial-server-stack107.sh'}
    assert after['native-target/reference-stack-probe103'] == before['native-target/reference-stack-probe103']
    for name in ('bootstrap-runtime087', 'bootstrap-runtime087.c', 'bootstrap', 'bootstrap.c'):
        assert (work / name).read_bytes() == (BUILD / 'commercial61-native-105' / name).read_bytes()
    assert after['early-hardware093.sh'][1] == before['early-hardware093.sh'][1].replace(sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1)
    key = 'native-target/commercial-desktop077.sh'
    assert after[key][1] == before[key][1].replace(b'/system/bin/sh /commercial-server-stack105.sh &\n', b'/system/bin/sh /commercial-server-stack107.sh &\n', 1)
    observer = (BASE / 'commercial-server-stack-107.sh').read_bytes()
    assert after['native-target/commercial-server-stack107.sh'] == (0o100755, observer)
    assert b'sleep 5' not in observer and b'hwstartupguide' not in observer
    assert observer.index(b'SERVER107_QUERY_EVENT') < observer.index(b'SERVER107_DFX_CALL_BEGIN')
    assert b'/system/bin/timeout 90 /system/bin/grep -E -m 1' in observer
    result = json.loads((report / 'result.json').read_text())
    for item in result['artifacts']:
        assert sha((work / item['name']).read_bytes()) == item['sha256']
    suite = subprocess.run(['python3', str(BASE / 'test-server-stack-107.py')], capture_output=True)
    (report / 'observer-tests.stdout').open('xb').write(suite.stdout)
    (report / 'observer-tests.stderr').open('xb').write(suite.stderr)
    assert suite.returncode == 0 and b'Ran 7 tests' in suite.stderr, suite.stderr.decode()
    subprocess.run(['/bin/sh', '-n', str(BASE / 'commercial-server-stack-107.sh')], check=True)
    guards = []
    with tempfile.TemporaryDirectory(prefix='commercial107-guards-') as directory:
        for name in ('init', 'bootstrap', 'bootstrap-runtime087'):
            executable = Path(directory) / name
            shutil.copyfile(work / name, executable)
            executable.chmod(0o755)
            run = subprocess.run(['qemu-aarch64', str(executable)], capture_output=True, timeout=15)
            assert run.returncode == 77, (name, run.returncode, run.stderr)
            guards.append(dict(name=name, status=77, stdout=run.stdout.decode(), stderr=run.stderr.decode()))
    overlay = json.loads((report / 'overlay-result.json').read_text())
    assert overlay['ordered_chain_equals_full_107']
    assert sha((work / 'minimal-overlay.img').read_bytes()) == overlay['sha256']
    assert (work / 'init.c').read_text().count('"commercial-server-stack107.log"') == 1
    assert '"commercial-server-stack105.log"' not in (work / 'init.c').read_text()
    admission = dict(only_declared_observation_delta=True, original_probe_and_runtime_byte_identical=True,
        original_services_identity_network_security_and_recovery_unchanged=True,
        reference_startup_script_unchanged=True, event_trigger_has_pid_filter_and_deadline=True,
        seven_observer_tests_pass=True, three_isolation_guards_pass=True,
        wrapper_only_tracks_new_outer_hash=True, ordered_chain_verified=True)
    output.open('x').write(json.dumps(admission, indent=2))
    (report / 'guard-tests.json').open('x').write(json.dumps(guards, indent=2))
    try:
        workflow = runpy.run_path(str(BASE / 'commercial-workflow-107.py'))
        for name in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
            source = workflow['source107'](name)
            compile(source, name, 'exec')
            assert 'StrictHostKeyChecking=yes' in source and 'commercial61-native-107' in source
            if name == 'install-commercial-native':
                parent = json.loads((ROOT / 'reports/commercial61-native-105/overlay-result.json').read_text())
                assert "assert sha(esp/'commercial61-native-105/initrd.img')==" + repr(parent['sha256']) in source
                assert "'initrd /commercial61-native-105/initrd.img','initrd /commercial61-native-107/initrd.img',options" in source
                runtime_hash = next(item['sha256'] for item in result['artifacts'] if item['name'] == 'bootstrap-runtime087')
                assert "assert sha(root/'bootstrap-runtime087')==" + repr(runtime_hash) in source
                assert '32*1024**2' in source and 'assert entry.stat().st_size<cluster' in source
                assert "sha(images/n)==m['sha256']" in source
            elif name == 'run-commercial-native':
                assert 'attempt_count=1' in source and 'no retries' in source and '660' in source
                assert "'enabled'" in source and "'active'" in source
            elif name == 'retrieve-commercial-evidence':
                previous = json.loads((ROOT / 'reports/commercial61-native-105/runtime-evidence/retrieval-manifest.json').read_text())['run']
                assert previous in source and 'ro,noload,nodev,nosuid,noexec' in source
                assert 'physical serial found; refusing export' in source and 'original UDID found; refusing export' in source
            else:
                assert 'user_authorized_old_entries_removed=removed_entries' in source
                assert 'commercial_original_images_unchanged=verified' in source
            (report / (name + '.generated.py')).open('x').write(source)
    except BaseException:
        output.rename(report / 'admission-test-failed.json')
        raise
    print(json.dumps(admission, indent=2))
