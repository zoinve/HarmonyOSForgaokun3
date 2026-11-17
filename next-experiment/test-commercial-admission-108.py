"""Verify scaffolding isolation, actual new-runtime loading and inherited gates."""
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
    work, report = BUILD / 'commercial61-native-108', ROOT / 'reports/commercial61-native-108'
    output = report / 'admission-test.json'
    assert not output.exists()
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def archive(number):
        return {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD / ('commercial61-native-' + number) / 'initrd.img').read_bytes()))}
    before, after = archive('107'), archive('108')
    assert {n for n in before if before[n] != after[n]} == {'init', 'early-hardware093.sh'}
    assert set(after) - set(before) == {'native-target/commercial-memmgr108.sh'}
    for name in ('native-target/reference-stack-probe103', 'native-target/commercial-server-stack107.sh',
                 'native-target/commercial-desktop077.sh', 'native-target/harmonymac-reference099.sh'):
        assert after[name] == before[name]
    builder = runpy.run_path(str(BASE / 'build-commercial-native-108.py'))
    parent = BUILD / 'commercial61-native-107'
    runtime = (work / 'bootstrap-runtime087.c').read_text()
    assert runtime == builder['runtime_source']((parent / 'bootstrap-runtime087.c').read_text())
    old_hash, new_hash = sha((parent / 'bootstrap-runtime087').read_bytes()), sha((work / 'bootstrap-runtime087').read_bytes())
    outer = (work / 'init.c').read_text()
    assert outer == builder['outer_source']((parent / 'init.c').read_text(), old_hash, new_hash)
    assert outer.count(builder['NEW_RUNTIME_PATH']) == 5 and builder['OLD_RUNTIME_PATH'] not in outer
    assert outer.count(new_hash) == 2 and old_hash not in outer
    assert (work / 'bootstrap').read_bytes() == (parent / 'bootstrap').read_bytes()
    assert (work / 'bootstrap.c').read_bytes() == (parent / 'bootstrap.c').read_bytes()
    assert runtime.index('volatile_ext4_data_037();') < runtime.index('    commercial_memmgr108();') < runtime.index('    native_persistent_capture030();')
    assert after['early-hardware093.sh'][1] == before['early-hardware093.sh'][1].replace(sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1)
    monitor = (BASE / 'commercial-memmgr-observer-108.sh').read_bytes()
    assert after['native-target/commercial-memmgr108.sh'] == (0o100755, monitor)
    assert all(token not in monitor for token in (b'force-stop', b'start_service', b'stop_service', b'param set', b'chmod', b'chown'))
    subprocess.run(['/bin/sh', '-n', str(BASE / 'commercial-memmgr-observer-108.sh')], check=True)
    result = json.loads((report / 'result.json').read_text())
    metadata = result['memmgr108']
    assert metadata['runtime_sha256'] == new_hash and metadata['runtime_path'] == builder['NEW_RUNTIME_PATH']
    assert result['external_runtime_bootstrap']['runtime_bootstrap_source'] == builder['NEW_RUNTIME_PATH']
    assert metadata['helper_sha256'] == sha((BASE / 'commercial-memmgr-prerequisites-108.h').read_bytes())
    assert metadata['helper_sha256'] == sha((report / 'commercial-memmgr-prerequisites-108.h').read_bytes())
    for item in result['artifacts']:
        assert sha((work / item['name']).read_bytes()) == item['sha256']
    for label, filename, count in [('helper', 'test-memmgr-prerequisites-108.py', 6), ('observer', 'test-server-stack-107.py', 7)]:
        suite = subprocess.run(['python3', str(BASE / filename)], capture_output=True)
        (report / (label + '-tests.stdout')).open('xb').write(suite.stdout)
        (report / (label + '-tests.stderr')).open('xb').write(suite.stderr)
        assert suite.returncode == 0 and ('Ran ' + str(count) + ' tests').encode() in suite.stderr, suite.stderr.decode()
    guards = []
    with tempfile.TemporaryDirectory(prefix='commercial108-guards-') as directory:
        for name in ('init', 'bootstrap', 'bootstrap-runtime087'):
            executable = Path(directory) / name
            shutil.copyfile(work / name, executable)
            executable.chmod(0o755)
            run = subprocess.run(['qemu-aarch64', str(executable)], capture_output=True, timeout=15)
            assert run.returncode == 77, (name, run.returncode, run.stderr)
            guards.append(dict(name=name, status=77, stdout=run.stdout.decode(), stderr=run.stderr.decode()))
    overlay = json.loads((report / 'overlay-result.json').read_text())
    assert overlay['ordered_chain_equals_full_108']
    assert sha((work / 'minimal-overlay.img').read_bytes()) == overlay['sha256']
    assert outer.count('"commercial-memmgr108.log"') == 1
    admission = dict(only_declared_scaffold_and_observation_delta=True,
        original_probe_startup_order_wrappers_and_services_unchanged=True,
        no_identity_setup_or_memory_metrics_fabricated=True, existing_event_observer_unchanged=True,
        six_real_c_helper_tests_pass=True, seven_existing_observer_tests_pass=True,
        new_runtime_actual_path_and_both_hash_checks_verified=True,
        runtime_helper_after_private_data_before_original_init=True,
        three_isolation_guards_pass=True, ordered_chain_verified=True)
    output.open('x').write(json.dumps(admission, indent=2))
    (report / 'guard-tests.json').open('x').write(json.dumps(guards, indent=2))
    try:
        workflow = runpy.run_path(str(BASE / 'commercial-workflow-108.py'))
        for name in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
            source = workflow['source108'](name)
            compile(source, name, 'exec')
            assert 'StrictHostKeyChecking=yes' in source and 'commercial61-native-108' in source
            if name == 'install-commercial-native':
                parent_overlay = json.loads((ROOT / 'reports/commercial61-native-107/overlay-result.json').read_text())
                assert "assert sha(esp/'commercial61-native-107/initrd.img')==" + repr(parent_overlay['sha256']) in source
                assert "'initrd /commercial61-native-107/initrd.img','initrd /commercial61-native-108/initrd.img',options" in source
                assert "assert sha(root/'bootstrap-runtime087')==" + repr(new_hash) in source
                assert "assert sha(root/'bootstrap-runtime087')==" + repr(old_hash) not in source
                assert '32*1024**2' in source and 'assert entry.stat().st_size<cluster' in source
                assert "sha(images/n)==m['sha256']" in source
            elif name == 'run-commercial-native':
                assert 'attempt_count=1' in source and 'no retries' in source and '660' in source
                assert "'enabled'" in source and "'active'" in source
            elif name == 'retrieve-commercial-evidence':
                previous = json.loads((ROOT / 'reports/commercial61-native-107/runtime-evidence/retrieval-manifest.json').read_text())['run']
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
