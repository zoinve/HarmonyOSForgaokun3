"""Exact delta, private RAM inputs, native BusyBox fixtures, export guards."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import re
import runpy
import stat
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def record(path, value):
    if path.exists():
        assert json.loads(path.read_text()) == value
    else:
        path.open('x').write(json.dumps(value, indent=2))


def main():
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    old, new = [{n: (m, d) for n, m, d in parse(gzip.decompress((BUILD/f'commercial61-native-{v}/initrd.img').read_bytes()))}
                for v in ('092', '093')]
    report = ROOT/'reports/commercial61-native-093'
    result = json.loads((report/'result.json').read_text())
    provenance = result['early_real_hardware_input']
    wrapper = new['early-hardware093.sh'][1].decode()
    parameter = 'native-target/graphics016/sys_prod/etc/param/hw_defaults.para'
    assert set(new) - set(old) == {'early-hardware093.sh'} and not set(old) - set(new)
    assert {n for n in old if old[n] != new[n]} == {'native-target/commercial-desktop077.sh'}
    for name, expected in [('init', provenance['original_core_sha256']), (parameter, provenance['original_parameter_sha256'])]:
        assert hashlib.sha256(new[name][1]).hexdigest() == expected
    assert hashlib.sha256(wrapper.encode()).hexdigest() == provenance['wrapper_sha256']
    assert new['native-target/native-hardware091'] == old['native-target/native-hardware091']
    assert 'mbedtls' not in wrapper and 'const.product.devUdid=' not in wrapper
    assert 'const.product.udid=' not in wrapper
    subprocess.run(['busybox', 'sh', '-n', str(report/'early-hardware093.sh')], check=True)
    subprocess.run(['busybox', 'sh', '-n', str(report/'diagnostic093.sh')], check=True)
    guard = subprocess.run(['busybox', 'sh', str(report/'early-hardware093.sh')], capture_output=True)
    assert guard.returncode == 77 and b'requires_pid1_root' in guard.stderr
    fixture_serial = b'AB12CD34EF56GH78'
    scenarios = []
    with tempfile.TemporaryDirectory(prefix='early093-tests-') as folder:
        folder = Path(folder)
        busybox = folder/'busybox'
        busybox.write_bytes(new['bin/busybox'][1])
        busybox.chmod(0o755)
        for case in ('valid', 'vendor-conflict', 'wrong-board', 'default-model', 'invalid-model',
                     'oversize-model', 'duplicate-key', 'hash-mismatch', 'wrong-fs', 'temp-collision',
                     'symlink-input', 'serial-mismatch', 'serial-invalid', 'serial-short', 'serial-hash-mismatch',
                     'existing-serial', 'existing-udid', 'existing-empty-serial', 'serial-symlink', 'temp-symlink'):
            root = folder/case
            dmi = root/'class/dmi/id'
            dmi.mkdir(parents=True)
            dt = root/'firmware/devicetree/base'
            dt.mkdir(parents=True)
            (dt/'model').write_bytes(b'Fixture Matebook E Go\0' if case != 'wrong-board' else b'Other board\0')
            (dmi/'sys_vendor').write_text('HUAWEI\n' if case != 'vendor-conflict' else 'OTHER\n')
            model = {'default-model': 'default', 'invalid-model': 'bad=model', 'oversize-model': 'X'*36}.get(case, 'TESTMODEL093')
            (dmi/'product_name').write_text(model+'\n')
            serial = {'serial-invalid': b'AB12CD34EF56GH7!', 'serial-short': b'AB12'}.get(case, fixture_serial)
            (dmi/'product_serial').write_bytes(serial+b'\n')
            (dmi/'chassis_serial').write_bytes((b'OTHER12345678901' if case == 'serial-mismatch' else serial)+b'\n')
            if case == 'serial-symlink':
                (root/'serial').write_bytes(serial+b'\n')
                (dmi/'product_serial').unlink()
                (dmi/'product_serial').symlink_to(root/'serial')
            data = old[parameter][1]
            data += {'duplicate-key': b'const.product.model=OTHER\n',
                     'existing-serial': b'ohos.boot.sn=EXISTING\n',
                     'existing-udid': b'const.product.devUdid=EXISTING\n',
                     'existing-empty-serial': b'ohos.boot.sn=\n'}.get(case, b'')
            para = root/'hardware.para'
            para.write_bytes(data)
            if case == 'symlink-input':
                link = root/'link.para'
                link.symlink_to(para)
                para = link
            temporary = Path(str(para)+'.early093')
            if case == 'temp-collision':
                temporary.write_text('keep\n')
            if case == 'temp-symlink':
                (root/'keep').write_text('keep\n')
                temporary.symlink_to(root/'keep')
            functions = wrapper.split('\nif [ "$$"', 1)[0].replace('/bin/busybox ', 'bb093 ')
            functions = functions.replace(provenance['original_parameter_sha256'],
                hashlib.sha256(data).hexdigest() if case != 'hash-mismatch' else '0'*64)
            functions = functions.replace(provenance['audited_physical_serial_sha256'],
                hashlib.sha256(fixture_serial).hexdigest() if case != 'serial-hash-mismatch' else '0'*64)
            dispatch = f'''bb093() {{
                if [ "$1" = stat ]; then echo {'0' if case == 'wrong-fs' else '62656572'}; return; fi
                if [ "$1" = chmod ]; then [ "$(stat -c %a "$3")" = 600 ] || return 90; fi
                qemu-aarch64 '{busybox}' "$@"
            }}
            '''
            process = subprocess.run(['busybox', 'sh', '-c', dispatch+functions+'\nprepare_hardware093 "$1" "$2"',
                'fixture', str(root), str(para)], capture_output=True)
            if case == 'valid':
                assert process.returncode == 0, process.stderr
                expected = data.replace(b'const.product.model=KLVU-WDU0\n', b'const.product.model=TESTMODEL093\n')
                expected += b'ohos.boot.sn='+fixture_serial+b'\n'
                assert para.read_bytes() == expected
                assert stat.S_IMODE(para.stat().st_mode) == 0o600
                assert b'original_init_owns_udid=1' in process.stdout
            else:
                assert process.returncode != 0, case
                assert para.read_bytes() == data, case
            assert fixture_serial not in process.stdout+process.stderr, case
            scenarios.append(dict(name=case, exit_status=process.returncode, passed=True))
        diagnostic = new['native-target/commercial-desktop077.sh'][1].decode()
        privacy = diagnostic.split('# Only a digest of the original parameter value enters evidence.\n', 1)[1].split('unset identity093 hash093\n', 1)[0]
        privacy = privacy.replace('/system/bin/param get const.product.devUdid', 'fixture_param').replace('/system/bin/tr', 'busybox tr').replace('/system/bin/sha256sum', 'busybox sha256sum')
        identity = b'abcdef0123456789'*4
        for name, value, status in [('valid-identity', identity, 0), ('short-identity', b'123', 0), ('denied-identity', b'', 1)]:
            command = 'fixture_param() { printf \'%s\\n\' "'+value.decode()+'"; return '+str(status)+'; }\n'+privacy
            observed = subprocess.check_output(['busybox', 'sh', '-c', command])
            if name == 'valid-identity':
                assert hashlib.sha256(identity.upper()+b'\n').hexdigest().encode() in observed
                assert identity not in observed and identity.upper() not in observed
            else:
                assert b'unavailable=1' in observed
            scenarios.append(dict(name=name, passed=True))
    overlay = json.loads((report/'overlay-result.json').read_text())
    assert overlay['bytes'] < 4096
    assert set(overlay['members']) == {'early-hardware093.sh', 'native-target/commercial-desktop077.sh'}
    assert overlay['chain'][-1] == 'commercial61-native-092/early093.img'
    checks = dict(exact_early_wrapper_and_diagnostic_delta=True, original_core_bootstrap_and_native_helper_unchanged=True,
        original_modules_packages_services_permissions_unchanged=True, archive_parameter_payload_unchanged=True,
        actual_firmware_model_and_matching_product_chassis_serial_only=True, audited_physical_serial_hash_required=True,
        no_substitute_identity_algorithm_or_provisioning_state=True, original_init_owns_udid_calculation=True,
        existing_parameter_identity_keys_refused=True, pid1_and_original_hash_guards=True,
        private_temporary_file_mode_before_chmod_verified=True, twenty_target_busybox_input_scenarios_pass=True,
        three_original_parameter_digest_scenarios_pass=True, no_raw_serial_or_udid_output=True,
        unchanged_native_identity_and_network_checks=True, overlay_under_one_4096_byte_cluster=True,
        shell_syntax_valid=True)
    record(report/'admission-test.json', checks)
    workflow = runpy.run_path(str(BASE/'commercial-workflow-093.py'))['source093']
    for action in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
        source = workflow(action)
        compile(source, '<workflow093>', 'exec')
        if action == 'install-commercial-native':
            assert 'rdinit=/early-hardware093.sh ' in source and '+2*cluster' in source
            assert 'assert shutil.disk_usage(esp).free>=32*1024**2' in source
            assert "dest=esp/'commercial61-native-092'" in source and "dest/'early093.img'" in source
        if action == 'retrieve-commercial-evidence':
            payload = next(node.value.value for node in ast.parse(source).body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == 'payload' for target in node.targets))
            compile(payload, '<remote-retrieval093>', 'exec')
            loop = next(node for node in ast.walk(ast.parse(payload)) if isinstance(node, ast.For)
                and isinstance(node.target, ast.Name) and node.target.id == 'p'
                and isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Attribute) and node.iter.func.attr == 'iterdir')
            code = compile(ast.Module(body=[loop], type_ignores=[]), '<exact-export-guard>', 'exec')
            with tempfile.TemporaryDirectory(prefix='export093-tests-') as folder:
                run = Path(folder)
                for name, body in [('clean', b'no identifiers'), ('serial', fixture_serial),
                    ('serial-split', b'Z'*(1024*1024-7)+fixture_serial), ('udid-upper', identity.upper()),
                    ('udid-lower', identity), ('udid-split', b'Z'*(1024*1024-20)+identity)]:
                    (run/'evidence').write_bytes(body)
                    namespace = dict(run=run, needles={fixture_serial},
                        identities={hashlib.sha256(identity.upper()+b'\n').hexdigest().encode()},
                        identity_pattern=re.compile(rb'(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])'), hashlib=hashlib)
                    rejected = False
                    try:
                        exec(code, namespace)
                    except AssertionError:
                        rejected = True
                    assert rejected == (name != 'clean'), name
                    scenarios.append(dict(name='export-'+name, rejected=rejected, passed=True))
    record(report/'early-hardware-scenarios.json', scenarios)
    record(report/'workflow-validation.json', dict(four_workflows_compile=True,
        six_exact_remote_export_guard_scenarios_pass=True, allocation_aware_32mib_guard=True,
        existing_directory_and_parent_payload_preserved=True))
    print(json.dumps(dict(admission=checks, scenarios=len(scenarios)), indent=2))


if __name__ == '__main__':
    main()
