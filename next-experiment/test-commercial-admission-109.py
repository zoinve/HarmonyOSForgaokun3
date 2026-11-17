"""Verify observation-only archive changes and preserved runtime boot checks."""
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
    work, report = BUILD / 'commercial61-native-109', ROOT / 'reports/commercial61-native-109'
    output = report / 'admission-test.json'
    assert not output.exists()
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def archive(number):
        return {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD / ('commercial61-native-' + number) / 'initrd.img').read_bytes()))}
    before, after = archive('108'), archive('109')
    assert set(before) <= set(after)
    assert {n for n in before if before[n] != after[n]} == {
        'init', 'early-hardware093.sh', 'native-target/commercial-memmgr108.sh'}
    assert set(after) - set(before) == {'native-target/commercial-memmgr-stack109.sh'}
    builder = runpy.run_path(str(BASE / 'build-commercial-native-109.py'))
    parent = BUILD / 'commercial61-native-108'
    outer = (work / 'init.c').read_text()
    assert outer == builder['outer_source']((parent / 'init.c').read_text())
    for filename in ('bootstrap-runtime087', 'bootstrap-runtime087.c', 'bootstrap', 'bootstrap.c'):
        assert (work / filename).read_bytes() == (parent / filename).read_bytes()
    runtime_hash = sha((work / 'bootstrap-runtime087').read_bytes())
    runtime_path = '/mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-108/bootstrap-runtime087'
    assert outer.count(runtime_path) == 5 and outer.count(runtime_hash) == 2
    assert '/commercial61-native-109/bootstrap-runtime087' not in outer
    assert after['early-hardware093.sh'][1] == before['early-hardware093.sh'][1].replace(
        sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1)
    monitor = builder['monitor_source'](before['native-target/commercial-memmgr108.sh'][1].decode()).encode()
    assert after['native-target/commercial-memmgr108.sh'] == (0o100755, monitor)
    observer = (BASE / 'commercial-memmgr-stack-109.sh').read_bytes()
    assert after['native-target/commercial-memmgr-stack109.sh'] == (0o100755, observer)
    assert sha(after['native-target/reference-stack-probe103'][1]) == 'bc9f14107ebfb682311bf8c714f148df579141bb443a358ff85199cdc443b181'
    for label, filename, count in [('memory-observer', 'test-memmgr-stack-109.py', 5),
                                  ('existing-observer', 'test-server-stack-107.py', 7),
                                  ('memory-helper', 'test-memmgr-prerequisites-108.py', 6)]:
        suite = subprocess.run(['python3', str(BASE / filename)], capture_output=True)
        (report / (label + '-tests.stdout')).open('xb').write(suite.stdout)
        (report / (label + '-tests.stderr')).open('xb').write(suite.stderr)
        assert suite.returncode == 0 and ('Ran ' + str(count) + ' tests').encode() in suite.stderr
    guards = []
    with tempfile.TemporaryDirectory(prefix='commercial109-guards-') as directory:
        for name in ('init', 'bootstrap', 'bootstrap-runtime087'):
            executable = Path(directory) / name
            shutil.copyfile(work / name, executable)
            executable.chmod(0o755)
            run = subprocess.run(['qemu-aarch64', str(executable)], capture_output=True, timeout=15)
            assert run.returncode == 77, (name, run.returncode)
            guards.append(dict(name=name, status=77))
    result = json.loads((report / 'result.json').read_text())
    for item in result['artifacts']:
        assert sha((work / item['name']).read_bytes()) == item['sha256']
    assert result['memstack109']['runtime_path'] == runtime_path
    assert result['memstack109']['runtime_sha256'] == runtime_hash
    assert result['external_runtime_bootstrap']['runtime_bootstrap_source'] == runtime_path
    assert outer.count('"commercial-memmgr-stack109.log"') == 1
    overlay = json.loads((report / 'overlay-result.json').read_text())
    assert overlay['ordered_chain_equals_full_109']
    assert sha((work / 'minimal-overlay.img').read_bytes()) == overlay['sha256']
    admission = dict(exact_observation_only_delta=True, original_services_tokens_and_recovery_unchanged=True,
        byte_identical_108_runtime_path_and_hash_checks_verified=True, dedicated_log_export_verified=True,
        eighteen_helper_and_observer_tests_pass=True, three_isolation_guards_pass=True,
        ordered_chain_verified=True, no_identity_setup_or_memory_metrics_fabricated=True)
    output.open('x').write(json.dumps(admission, indent=2))
    (report / 'guard-tests.json').open('x').write(json.dumps(guards, indent=2))
    try:
        workflow = runpy.run_path(str(BASE / 'commercial-workflow-109.py'))
        for name in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
            source = workflow['source109'](name)
            compile(source, name, 'exec')
            assert 'StrictHostKeyChecking=yes' in source and 'commercial61-native-109' in source
            if name == 'install-commercial-native':
                assert "'initrd /commercial61-native-108/initrd.img','initrd /commercial61-native-109/initrd.img',options" in source
                assert repr(runtime_path.removeprefix('/mnt/ubuntu')) in source
                assert '32*1024**2' in source and 'entry.stat().st_size<cluster' in source
            elif name == 'run-commercial-native':
                assert 'attempt_count=1' in source and '660' in source
            elif name == 'retrieve-commercial-evidence':
                previous = json.loads((ROOT / 'reports/commercial61-native-108/runtime-evidence/retrieval-manifest.json').read_text())['run']
                assert previous in source and 'ro,noload,nodev,nosuid,noexec' in source
                assert 'original UDID found; refusing export' in source
            else:
                assert 'user_authorized_old_entries_removed=removed_entries' in source
                assert 'commercial_original_images_unchanged=verified' in source
            (report / (name + '.generated.py')).open('x').write(source)
    except BaseException:
        output.rename(report / 'admission-test-failed.json')
        raise
    print(json.dumps(admission, indent=2))
