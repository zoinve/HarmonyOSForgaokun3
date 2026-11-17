"""Verify the exact experimental kernel and reference fixture limitations."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883/native-binder-kernel-045')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


if __name__ == '__main__':
    output = ROOT / 'reports/real-memcg-requirements-audit-110.json'
    assert not output.exists()
    original = json.loads((ROOT / 'reports/native-binder-kernel-045/result.json').read_text())
    config = BUILD / 'out/.config'
    image = BUILD / 'out/arch/arm64/boot/Image'
    assert sha(config) == original['config_sha256']
    assert sha(image) == original['sha256']
    body = config.read_text()
    assert 'CONFIG_MEMCG=y\n' in body and '# CONFIG_MEMCG_V1 is not set\n' in body
    inspected = []
    names = ['memory.app_score', 'memory.name', 'memory.zswapd_single_memcg_param']
    tokens = ['app_score', 'zswapd_single_memcg_param']
    for name in ('mm/memcontrol.c', 'mm/memcontrol-v1.c', 'include/linux/memcontrol.h', 'include/linux/memcontrol-v1.h'):
        path = BUILD / 'linux' / name
        if path.is_file():
            text = path.read_text()
            inspected.append(dict(source=name, sha256=sha(path),
                required_extension_tokens_found=[token for token in tokens if token in text]))
    assert inspected and not any(item['required_extension_tokens_found'] for item in inspected)
    fixture = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/tools/prepare-init-service-test.sh')
    text = fixture.read_text()
    assert 'Diagnostic-only placeholders.' in text
    assert 'test -e /dev/memcg/$f || echo 0 > /dev/memcg/$f' in text
    assert all(name in text for name in names)
    result = dict(experimental_kernel_sha256=sha(image), experimental_config_sha256=sha(config),
        config=dict(MEMCG=True, MEMCG_V1=False), inspected_sources=inspected,
        required_interfaces=names, required_vendor_extensions_absent_from_inspected_sources=True,
        enabling_standard_memcg_v1_alone_not_a_complete_interface_fix=True,
        reference_fixture_path=str(fixture), reference_fixture_sha256=sha(fixture),
        reference_fixture_explicitly_uses_diagnostic_regular_file_placeholders=True,
        reference_fixture_not_proof_of_real_memory_service_semantics=True,
        original_service_init_failure_proven_in109=True,
        target_boot_performed=False, kernel_or_images_modified=False,
        next_fix_must_supply_real_interface_semantics_or_supported_original_nonvendor_mode=True,
        desktop_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
