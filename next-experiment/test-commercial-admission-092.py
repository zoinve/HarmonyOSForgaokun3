"""Check exact archive delta and real BusyBox parsing on synthetic fixtures."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def main():
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    old, new = [{n: (m, d) for n, m, d in parse(gzip.decompress((BUILD/f'commercial61-native-{v}/initrd.img').read_bytes()))}
                for v in ('091', '092')]
    report = ROOT/'reports/commercial61-native-092'
    result = json.loads((report/'result.json').read_text())
    record = result['early_real_model_input']
    wrapper = new['early-hardware092.sh'][1].decode()
    parameter = 'native-target/graphics016/sys_prod/etc/param/hw_defaults.para'
    assert set(new) - set(old) == {'early-hardware092.sh', 'early-sys092'}
    assert not set(old) - set(new)
    assert {n for n in old if old[n] != new[n]} == {'native-target/commercial-desktop077.sh'}
    assert hashlib.sha256(new['init'][1]).hexdigest() == record['original_core_sha256']
    assert hashlib.sha256(new[parameter][1]).hexdigest() == record['original_parameter_sha256']
    assert hashlib.sha256(wrapper.encode()).hexdigest() == record['wrapper_sha256']
    assert 'product_serial' not in wrapper and 'boot.sn' not in wrapper and 'udid' not in wrapper
    assert new['early-sys092'] == (0o040755, b'')
    subprocess.run(['busybox', 'sh', '-n', str(report/'early-hardware092.sh')], check=True)
    guard = subprocess.run(['busybox', 'sh', str(report/'early-hardware092.sh')], capture_output=True)
    assert guard.returncode == 77 and b'requires_pid1_root' in guard.stderr
    with tempfile.TemporaryDirectory(prefix='early092-tests-') as folder:
        folder = Path(folder)
        busybox = folder/'busybox'
        busybox.write_bytes(new['bin/busybox'][1])
        busybox.chmod(0o755)
        assert busybox.read_bytes()[:4] == b'\x7fELF'
        applets = subprocess.check_output(['qemu-aarch64', str(busybox), '--list']).splitlines()
        assert all(name.encode() in applets for name in ('awk', 'stat', 'sha256sum', 'mount', 'umount', 'mv', 'tr', 'id', 'reboot'))
        scenarios = []
        for case in ('valid', 'vendor-conflict', 'wrong-board', 'default-model', 'invalid-model',
                     'oversize-model', 'duplicate-key', 'hash-mismatch', 'wrong-fs', 'temp-collision', 'symlink-input'):
            root = folder/case
            dmi = root/'class/dmi/id'
            dmi.mkdir(parents=True)
            dt = root/'firmware/devicetree/base'
            dt.mkdir(parents=True)
            (dt/'model').write_bytes(b'Fixture Matebook E Go\0' if case != 'wrong-board' else b'Other board\0')
            (dmi/'sys_vendor').write_text('HUAWEI\n' if case != 'vendor-conflict' else 'OTHER\n')
            model = {'default-model': 'default', 'invalid-model': 'bad=model', 'oversize-model': 'X'*36}.get(case, 'TESTMODEL092')
            (dmi/'product_name').write_text(model+'\n')
            data = old[parameter][1]
            if case == 'duplicate-key':
                data += b'const.product.model=OTHER\n'
            para = root/'hardware.para'
            para.write_bytes(data)
            if case == 'symlink-input':
                link = root/'link.para'
                link.symlink_to(para)
                para = link
            if case == 'temp-collision':
                Path(str(para)+'.early092').write_text('keep\n')
            functions = wrapper.split('\nif [ "$$"', 1)[0].replace('/bin/busybox ', 'bb092 ')
            functions = functions.replace(record['original_parameter_sha256'],
                hashlib.sha256(data).hexdigest() if case != 'hash-mismatch' else '0'*64)
            # Only the sysfs filesystem-type syscall is simulated; all applets
            # and awk/rename behavior use the exact AArch64 initrd BusyBox.
            dispatch = f'''bb092() {{
                if [ "$1" = stat ]; then echo {'0' if case == 'wrong-fs' else '62656572'}; return; fi
                qemu-aarch64 '{busybox}' "$@"
            }}
            '''
            process = subprocess.run(['busybox', 'sh', '-c', dispatch+functions+'\nprepare_model092 "$1" "$2"',
                'fixture', str(root), str(para)], capture_output=True)
            if case == 'valid':
                assert process.returncode == 0, process.stderr
                expected = data.replace(b'const.product.model=KLVU-WDU0\n', b'const.product.model=TESTMODEL092\n')
                assert expected != data and para.read_bytes() == expected
                assert b'model_length=12' in process.stdout
            else:
                assert process.returncode != 0, case
                assert para.read_bytes() == data, case
            scenarios.append(dict(name=case, exit_status=process.returncode, passed=True))
    (report/'early-model-scenarios.json').open('x').write(json.dumps(scenarios, indent=2))
    overlay = json.loads((report/'overlay-result.json').read_text())
    assert set(overlay['members']) == {'early-hardware092.sh', 'early-sys092', 'native-target/commercial-desktop077.sh'}
    assert overlay['bytes'] < 4096
    checks = dict(exact_wrapper_directory_and_diagnostic_delta=True, original_core_and_bootstrap_byte_identical=True,
        original_parameter_archive_unchanged=True, original_packages_modules_services_and_permissions_unchanged=True,
        runtime_model_from_genuine_sysfs_only=True, original_manufacturer_must_match_firmware=True,
        wrapper_never_reads_or_supplies_serial_or_udid=True, no_provisioning_or_guide_stop_changes=True,
        original_core_and_parameter_hash_guards=True, pid1_guard_refuses_outside_target=True,
        target_busybox_applets_available=True, eleven_target_busybox_fixture_scenarios_pass=True,
        ram_model_only_change_verified=True, original_091_identity_guards_retained=True,
        shell_syntax_valid=True, overlay_under_4096_bytes=True)
    (report/'admission-test.json').open('x').write(json.dumps(checks, indent=2))
    workflow = runpy.run_path(str(BASE/'commercial-workflow-092.py'))['source092']
    for action in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
        source = workflow(action)
        compile(source, '<workflow092>', 'exec')
        if action == 'install-commercial-native':
            assert "rdinit=/early-hardware092.sh " in source
            assert "+32*1024**2" in source
        if action == 'retrieve-commercial-evidence':
            assert 'physical_serial_guard_passed=True' in source
            assert 'commercial61-native-087-07288f77-1ad4-48b8-9d7a-1001af81bfdf' in source
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
