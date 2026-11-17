"""Independently replay all29 archives and validate the new lifecycle/storage gates."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import lzma
import runpy
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')
REPORT = ROOT / 'reports/commercial61-native-235'


def sha(data):
    return hashlib.sha256(data).hexdigest()


if __name__ == '__main__':
    assert not (REPORT / 'admission-test.json').exists()
    logs = REPORT / 'admission-001'
    assert not logs.exists()
    logs.mkdir()
    work = BUILD / 'commercial61-native-235'
    parent = BUILD / 'commercial61-native-206'
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def unpack(path):
        data = path.read_bytes()
        raw = lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {name: (mode, payload) for name, mode, payload in parser(raw)}
    metadata = json.loads((REPORT / 'result.json').read_text())
    for row in metadata['artifacts']:
        assert sha((work / row['name']).read_bytes()) == row['sha256']
    before, after = unpack(parent / 'initrd.img'), unpack(work / 'initrd.img')
    assert before.keys() == after.keys()
    assert {name for name in before if before[name] != after[name]} == {'init', 'early-hardware093.sh'}
    for name in ['bootstrap-runtime087', 'bootstrap-runtime087.c', 'bootstrap', 'bootstrap.c', 'native-usb153', 'live-debug164', 'live-debug159']:
        assert (work / name).read_bytes() == (parent / name).read_bytes()
    adapt = runpy.run_path(str(BASE / 'settings-native-235.py'))
    assert (work / 'init.c').read_text() == adapt['outer235']((parent / 'init.c').read_text())
    for name, digest in metadata['settings235']['header_hashes'].items():
        assert (work / name).read_bytes() == (parent / name).read_bytes()
        assert sha((work / name).read_bytes()) == digest
    assert metadata['settings235']['original_aa_launch_requests'] == 0
    repair = json.loads((ROOT / 'reports/settingsdata-orphan-repair-234/result.json').read_text())
    assert repair['final_read_only_fsck_exit'] == 0 and repair['existing_tree_before'] == repair['existing_tree_after']
    assert metadata['settings235']['expected_preboot_candidate_sha256'] == repair['candidate_after_sha256']
    with tempfile.TemporaryDirectory(prefix='rebuild235-') as directory:
        for name in ['init', 'bootstrap-runtime087']:
            binary = Path(directory) / name
            args = ['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(BASE), str(work / (name + '.c'))]
            if name == 'init':
                args.append(str(BASE / 'baremetal-diagnostic-core.c'))
            proc = subprocess.run(args + ['-o', str(binary)], capture_output=True, timeout=120)
            assert proc.returncode == 0, proc.stderr.decode()
            assert binary.read_bytes() == (work / name).read_bytes()
            proc = subprocess.run(['qemu-aarch64', str(binary)], capture_output=True, timeout=15)
            assert proc.returncode == 77, (name, proc.returncode, proc.stderr)
    overlay = json.loads((REPORT / 'overlay-result.json').read_text())
    assert len(overlay['chain']) == 29
    assert set(unpack(work / 'minimal-overlay.img')) == {'init', 'early-hardware093.sh', 'live-debug159'}
    merged = {}
    for relative in overlay['chain']:
        number, filename = relative.split('/')
        if number == 'commercial61-native-235':
            path = work / 'minimal-overlay.img'
        elif number == 'commercial61-native-001':
            path = BUILD / relative
        elif number == 'commercial61-native-016':
            path = BUILD / 'commercial61-native-016-r2/minimal-overlay.img'
        elif number == 'commercial61-native-072':
            path = BUILD / number / 'minimal-overlay-xz.img'
        else:
            path = BUILD / number / 'minimal-overlay.img'
        merged.update(unpack(path))
    assert merged == after
    assert all(not name.endswith('host_ed25519') for name in after)
    tests = ['test-settings-native-235.py', 'test-cleaned-evidence-227.py',
        'test-persistent-runtime-173.py', 'test-persistent-lifecycle-172.py', 'test-persistent-runtime-168.py',
        'test-persistent-data-166.py', 'test-live-debug-log-163.py', 'test-live-debug-loader-164.py',
        'test-live-debug-storage-161.py', 'test-live-debug-analysis-164.py', 'test-live-debug-root-158.py',
        'test-live-debug-address-159.py', 'test-live-debug-discovery-159.py', 'test-live-debug-reader-156.py',
        'test-native-service-devices-152.py', 'test-native-input-usb-148.py', 'test-native-driver-133.py',
        'test-gaokun-basic-sysfs-001.py', 'test-native-backlight-129.py', 'test-oobe-seed-123.py']
    for name in tests:
        proc = subprocess.run(['python3', str(BASE / name)], capture_output=True, timeout=120)
        (logs / (name + '.txt')).open('xb').write(proc.stdout + proc.stderr)
        assert proc.returncode == 0 and b'Ran 0 tests' not in proc.stderr, (name, proc.stderr.decode())
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-235.py'))
    for operation in workflow['OPERATIONS']:
        source = workflow['source235'](operation)
        compile(source, operation, 'exec')
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and '\nfrom pathlib import Path\n' in node.value:
                compile(node.value, operation + '-remote', 'exec')
        assert 'StrictHostKeyChecking=yes' in source and 'usb176_preflight' not in source
        if operation == 'install-commercial-native':
            assert source.index('assert estimated235<1800') < source.index('root.mkdir()')
            assert source.index('settings235_preflight()\n') < source.index('root.mkdir()')
            assert '32*1024**2' in source and 'harmony.persistent_data166=1' in source
            assert 'AUTO RETURN 900 SEC' in source
        elif operation == 'run-commercial-native':
            assert 'attempt_count=1' in source and '1260' in source and 'set235.img' in source
            assert repair['candidate_after_sha256'] in source
        elif operation == 'retrieve-commercial-evidence':
            assert 'ro,noload' in source and '0<len(phases)<=2' in source
            assert "with (dest/'original.tar')" not in source
            run = json.loads((ROOT / 'reports/commercial61-native-206/runtime-evidence/retrieval-manifest.json').read_text())['run']
            assert run in source
            assert 'physical serial found; refusing export' in source and 'original UDID found; refusing export' in source
        (REPORT / (operation + '.generated.py')).open('x').write(source)
    result = dict(exact_two_member_init_delta=True, desktop173_runtime_and_source_byte_identical=True,
        isolated_candidate_fsck_and_tree_preservation=True, complete29_archive_chain_independently_equals_full=True,
        reproducible_binaries_and_non_pid1_guards=True, twenty_focused_scripts_pass=True,
        workflow_and_remote_sources_compile=True, real_namespace_pin_and_non_reaping_sampling_tested=True,
        snapshot_retention_and_no_duplicate_tar_verified=True, original_security_and_usb_checkpoint_preserved=True)
    (REPORT / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
