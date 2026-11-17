"""Verify exact helper/script delta and unchanged original security boundaries."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def main():
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    old, new = [{n: (m, d) for n, m, d in parse(gzip.decompress((BUILD/f'commercial61-native-{v}/initrd.img').read_bytes()))}
                for v in ('090', '091')]
    binary = 'native-target/native-hardware091'
    script = 'native-target/commercial-desktop077.sh'
    assert set(new) - set(old) == {binary} and not set(old) - set(new)
    assert {n for n in old if old[n] != new[n]} == {script}
    assert new[binary][0] == 0o100755
    report = ROOT/'reports/commercial61-native-091'
    result = json.loads((report/'result.json').read_text())
    provenance = result['hardware_input_diagnostic']
    assert hashlib.sha256(new[binary][1]).hexdigest() == provenance['helper_sha256']
    source = (BASE/'native-hardware-091.c').read_text()
    assert hashlib.sha256(source.encode()).hexdigest() == provenance['source_sha256']
    assert source.count('set("ohos.boot.sn", serial)') == 1
    assert not any(word in source for word in ('set("const.', 'CalcDevUdid', 'GetSha256Value', 'mbedtls_sha256',
                                               'SetCalling', 'SetToken', 'SetUid', 'device_provisioned', 'user_setup_complete'))
    assert 'RTLD_NOW | RTLD_LOCAL' in source
    assert '/sys/class/dmi/id/product_serial' in source and '/sys/class/dmi/id/chassis_serial' in source
    assert '0x62656572UL' in source
    assert '!strcmp(values[3], vendor) && !strcmp(values[4], model)' in source
    assert 'GetParameter' in source and 'SetParameter' in source and 'GetDevUdid' in source
    assert b'no_write_requested=1' in new[binary][1]
    assert b'libc.so.6' not in (report/'dynamic.txt').read_bytes()
    expected = runpy.run_path(str(BASE/'build-commercial-native-091.py'))['script091'](provenance['helper_sha256'])
    assert new[script][1] == expected
    assert b'/system/bin/timeout 8 /native-hardware091' in expected
    assert provenance['original_module_sha256'].encode() in expected
    subprocess.run(['sh', '-n', str(report/'diagnostic091.sh')], check=True)
    assert b'8 identity decision scenarios PASS' in (report/'decision-tests.stdout').read_bytes()
    overlay = json.loads((report/'overlay-result.json').read_text())
    assert set(overlay['members']) == {binary, script} and overlay['bytes'] < 14000
    checks = dict(exact_owned_helper_and_script_delta=True, original_packages_images_and_modules_unchanged=True,
        original_services_permissions_and_tokens_unchanged=True, original_parameter_apis_and_module_only=True,
        no_substitute_udid_or_identity_algorithm=True, no_existing_identity_overwrite=True,
        product_metadata_and_serial_source_match_required=True, actual_sysfs_firmware_source_required=True,
        single_missing_serial_supply_only=True, no_provisioning_or_guide_stop_changes=True,
        no_raw_identity_value_logging=True, original_module_and_helper_runtime_hash_guards=True,
        eight_decision_scenarios_pass=True, original_network_observation_retained=True,
        platform_elf_without_glibc=True, bounded_command_and_shell_syntax=True,
        measured_small_overlay=True)
    (report/'admission-test.json').open('x').write(json.dumps(checks, indent=2))
    workflow = runpy.run_path(str(BASE/'commercial-workflow-091.py'))['source091']
    for action in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
        text = workflow(action)
        compile(text, '<workflow091>', 'exec')
        if action == 'retrieve-commercial-evidence':
            for number in ('087', '088', '089', '090'):
                run = json.loads((ROOT/f'reports/commercial61-native-{number}/runtime-evidence/retrieval-manifest.json').read_text())['run']
                assert run in text
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
