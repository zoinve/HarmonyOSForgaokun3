"""Admit only the isolated DFX observation and independent export delta."""
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


if __name__ == '__main__':
    report, work = ROOT/'reports/commercial61-native-104', BUILD/'commercial61-native-104'
    output = report/'admission-test.json'
    assert not output.exists()
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    builder = runpy.run_path(str(BASE/'build-commercial-native-104.py'))
    sha = builder['sha']
    def archive(number):
        return {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD/f'commercial61-native-{number}/initrd.img').read_bytes()))}
    before, after = archive('101'), archive('104')
    assert {n for n in before if before[n] != after[n]} == {'init', 'early-hardware093.sh', 'native-target/commercial-desktop077.sh'}
    assert set(after)-set(before) == {'native-target/reference-stack-probe103', 'native-target/commercial-server-stack104.sh'}
    result = json.loads((report/'result.json').read_text())
    delta = result['server_stack104']
    assert (work/'init.c').read_text() == builder['outer_source']((BUILD/'commercial61-native-101/init.c').read_text())
    for name in ('bootstrap-runtime087', 'bootstrap-runtime087.c', 'bootstrap', 'bootstrap.c'):
        assert (work/name).read_bytes() == (BUILD/'commercial61-native-101'/name).read_bytes()
    assert after['early-hardware093.sh'][1] == before['early-hardware093.sh'][1].replace(sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1)
    key = 'native-target/commercial-desktop077.sh'
    anchor = b'/system/bin/sh /commercial-softbus-observer101.sh &\n'
    assert after[key][1] == before[key][1].replace(anchor, b'/system/bin/sh /commercial-server-stack104.sh &\n'+anchor, 1)
    observer = (BASE/'commercial-server-stack-104.sh').read_bytes()
    assert after['native-target/commercial-server-stack104.sh'] == (0o100755, observer)
    assert after['native-target/reference-stack-probe103'] == (0o100755, (BUILD/'reference-stack-probe-103/app-stack-probe').read_bytes())
    assert sha(observer) == delta['observer_sha256']
    for item in result['artifacts']:
        assert sha((work/item['name']).read_bytes()) == item['sha256']
    shell = subprocess.run(['python3', str(BASE/'test-server-stack-104.py')], capture_output=True)
    (report/'observer-tests.stdout').open('xb').write(shell.stdout)
    (report/'observer-tests.stderr').open('xb').write(shell.stderr)
    assert shell.returncode == 0, shell.stderr.decode()
    subprocess.run(['/bin/sh', '-n', str(report/'observer104.sh')], check=True)
    guards = []
    with tempfile.TemporaryDirectory(prefix='commercial104-guards-') as directory:
        for name in ('init', 'bootstrap', 'bootstrap-runtime087'):
            executable = Path(directory)/name
            shutil.copyfile(work/name, executable)
            executable.chmod(0o755)
            run = subprocess.run(['qemu-aarch64', str(executable)], capture_output=True, timeout=15)
            assert run.returncode == 77, (name, run.returncode, run.stderr)
            guards.append(dict(name=name, status=77, stdout=run.stdout.decode(), stderr=run.stderr.decode()))
    overlay = json.loads((report/'overlay-result.json').read_text())
    assert overlay['ordered_chain_equals_full_104']
    assert overlay['bytes'] == (work/'minimal-overlay.img').stat().st_size
    assert overlay['sha256'] == sha((work/'minimal-overlay.img').read_bytes())
    admission = dict(only_declared_ram_changes=True, original_reference_probe_byte_identical=True,
        original_services_identity_network_security_and_recovery_unchanged=True,
        unchanged_runtime_bootstrap_and_reference_startup_order=True,
        wrapper_only_tracks_new_outer_hash=True, six_observer_scenario_tests_pass=True,
        independent_log_has_one_owner_and_bounded_export=True,
        three_isolation_guards_pass=True, ordered_chain_verified=True)
    assert 'exec > /data/commercial-server-stack104.log' in observer.decode()
    assert observer.count(b'commercial-server-stack104.log') == 1
    assert (work/'init.c').read_text().count('"commercial-server-stack104.log"') == 1
    output.open('x').write(json.dumps(admission, indent=2))
    (report/'guard-tests.json').open('x').write(json.dumps(guards, indent=2))
    try:
        workflow = runpy.run_path(str(BASE/'commercial-workflow-104.py'))
        for name in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
            source = workflow['source104'](name)
            compile(source, name, 'exec')
            assert 'StrictHostKeyChecking=yes' in source and 'commercial61-native-104' in source
            if name == 'install-commercial-native':
                parent = json.loads((ROOT/'reports/commercial61-native-101/overlay-result.json').read_text())
                assert "assert sha(esp/'commercial61-native-101/initrd.img')=="+repr(parent['sha256']) in source
                assert "'initrd /commercial61-native-101/initrd.img','initrd /commercial61-native-104/initrd.img',options" in source
                runtime_hash = next(i['sha256'] for i in result['artifacts'] if i['name'] == 'bootstrap-runtime087')
                assert "assert sha(root/'bootstrap-runtime087')=="+repr(runtime_hash) in source
                assert '32*1024**2' in source and 'assert entry.stat().st_size<cluster' in source
                assert "sha(images/n)==m['sha256']" in source
            if name == 'run-commercial-native':
                assert 'attempt_count=1' in source and 'no retries' in source and '660' in source
                assert "'enabled'" in source and "'active'" in source
            if name == 'retrieve-commercial-evidence':
                previous = json.loads((ROOT/'reports/commercial61-native-101/runtime-evidence/retrieval-manifest.json').read_text())['run']
                assert previous in source and 'ro,noload,nodev,nosuid,noexec' in source
                assert 'physical serial found; refusing export' in source and 'original UDID found; refusing export' in source
            if name == 'verify-commercial-return':
                assert 'user_authorized_old_entries_removed=removed_entries' in source
                assert 'commercial_original_images_unchanged=verified' in source
            (report/(name+'.generated.py')).open('x').write(source)
    except BaseException:
        output.rename(report/'admission-test-failed.json')
        raise
    print(json.dumps(admission, indent=2))
