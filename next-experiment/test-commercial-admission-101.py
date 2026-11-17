"""Admit only the declared 101 service delta with all inherited safety gates."""
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
    report, work = ROOT/'reports/commercial61-native-101', BUILD/'commercial61-native-101'
    output = report/'admission-test.json'
    assert not output.exists()
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    builder = runpy.run_path(str(BASE/'build-commercial-native-101.py'))
    sha = builder['sha']
    def archive(number):
        return {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD/f'commercial61-native-{number}/initrd.img').read_bytes()))}
    before, after = archive('099'), archive('101')
    allowed = {'init', 'early-hardware093.sh', 'native-target/commercial-desktop077.sh'}
    assert {n for n in before if before[n] != after[n]} == allowed
    assert set(after)-set(before) == {'native-target/softbus-reference101.cfg', 'native-target/commercial-softbus-observer101.sh'}
    result = json.loads((report/'result.json').read_text())
    delta = result['softbus_reference101']
    original = (report/'softbus-original.cfg').read_bytes()
    updated = builder['adapt_config'](original)
    assert after['native-target/softbus-reference101.cfg'] == (0o100644, updated)
    assert sha(updated) == delta['adapted_config_sha256']
    assert after['early-hardware093.sh'][1] == before['early-hardware093.sh'][1].replace(sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1)
    key = 'native-target/commercial-desktop077.sh'
    anchor = b'/system/bin/sh /commercial-reference-observer099.sh &\n'
    assert after[key][1] == before[key][1].replace(anchor, b'/system/bin/sh /commercial-softbus-observer101.sh &\n'+anchor, 1)
    observer = (BASE/'commercial-softbus-observer-101.sh').read_bytes().replace(b'CONFIG_SHA', sha(updated).encode())
    assert after['native-target/commercial-softbus-observer101.sh'] == (0o100755, observer)
    assert (work/'bootstrap-runtime087.c').read_text() == builder['inner_source']((BUILD/'commercial61-native-099/bootstrap-runtime087.c').read_text(), sha(updated))
    outer = (BUILD/'commercial61-native-099/init.c').read_text()
    parent_hash = sha((BUILD/'commercial61-native-099/bootstrap-runtime087').read_bytes())
    path = '/mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-087/bootstrap-runtime087'
    assert (work/'init.c').read_text() == outer.replace(path, path.replace('commercial61-native-087/', 'commercial61-native-101/')).replace(parent_hash, delta['runtime_sha256'])
    for item in result['artifacts']:
        assert sha((work/item['name']).read_bytes()) == item['sha256']
    subprocess.run(['python3', str(BASE/'test-commercial-softbus-101.py')], check=True)
    guards = []
    with tempfile.TemporaryDirectory(prefix='commercial101-guards-') as directory:
        for name in ('init', 'bootstrap', 'bootstrap-runtime087'):
            executable = Path(directory)/name
            shutil.copyfile(work/name, executable)
            executable.chmod(0o755)
            run = subprocess.run(['qemu-aarch64', str(executable)], capture_output=True)
            assert run.returncode == 77, (name, run.returncode, run.stderr)
            guards.append(dict(name=name, status=77, temporary_copy_matches_deployed_mode=True))
    subprocess.run(['/bin/sh', '-n', str(report/'observer101.sh')], check=True)
    overlay = json.loads((report/'overlay-result.json').read_text())
    assert overlay['ordered_chain_equals_full_101']
    assert overlay['bytes'] == (work/'minimal-overlay.img').stat().st_size
    assert overlay['sha256'] == sha((work/'minimal-overlay.img').read_bytes())
    admission = dict(only_declared_ram_changes=True, stock_service_permissions_and_jobs_identical=True,
        exact_reference_preload_removal=True, identity_network_security_and_recovery_unchanged=True,
        unchanged_reference_stop_and_startup_order=True, wrapper_only_tracks_new_outer_hash=True,
        eight_config_and_source_tests_pass=True, three_isolation_guards_pass=True, ordered_chain_verified=True)
    output.open('x').write(json.dumps(admission, indent=2))
    (report/'guard-tests.json').open('x').write(json.dumps(guards, indent=2))
    try:
        workflow = runpy.run_path(str(BASE/'commercial-workflow-101.py'))
        for name in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
            source = workflow['source101'](name)
            compile(source, name, 'exec')
            assert 'StrictHostKeyChecking=yes' in source and 'commercial61-native-101' in source
            if name == 'install-commercial-native':
                parent = json.loads((ROOT/'reports/commercial61-native-099/overlay-result.json').read_text())
                assert "assert sha(esp/'commercial61-native-099/initrd.img')=="+repr(parent['sha256']) in source
                assert "'initrd /commercial61-native-099/initrd.img','initrd /commercial61-native-101/initrd.img',options" in source
                assert "assert sha(root/'bootstrap-runtime087')=="+repr(delta['runtime_sha256']) in source
                assert '32*1024**2' in source and 'assert entry.stat().st_size<cluster' in source
                assert "sha(images/n)==m['sha256']" in source
            if name == 'run-commercial-native':
                assert 'attempt_count=1' in source and 'no retries' in source and '660' in source
                assert "'enabled'" in source and "'active'" in source
            if name == 'retrieve-commercial-evidence':
                old_run = json.loads((ROOT/'reports/commercial61-native-099/runtime-evidence/retrieval-manifest.json').read_text())['run']
                assert old_run in source and 'ro,noload,nodev,nosuid,noexec' in source
                assert 'physical serial found; refusing export' in source and 'original UDID found; refusing export' in source
            if name == 'verify-commercial-return':
                assert 'user_authorized_old_entries_removed=removed_entries' in source
                assert 'commercial_original_images_unchanged=verified' in source
            (report/(name+'.generated.py')).open('x').write(source)
    except BaseException:
        output.rename(report/'admission-test-failed.json')
        raise
    print(json.dumps(admission, indent=2))
