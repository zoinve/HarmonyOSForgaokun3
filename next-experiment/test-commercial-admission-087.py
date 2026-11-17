"""Check exact archive delta, supported JSON path and guarded RAM sidecar."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')


def main():
    parse = runpy.run_path(str(ROOT / 'next-experiment/audit-commercial-network-inputs-079.py'))['members']
    old, new = [{n: (m, d) for n, m, d in parse(gzip.decompress((BUILD / f'commercial61-native-{number}/initrd.img').read_bytes()))}
                for number in ('086', '087')]
    assert set(old) == set(new)
    assert {n for n in old if old[n] != new[n]} == {'init'}
    folder = ROOT / 'reports/commercial61-native-087'
    record = json.loads((folder / 'workspace-provenance.json').read_text())
    inner = (BUILD / 'commercial61-native-087/bootstrap-runtime087.c').read_text()
    original = (BUILD / 'commercial61-native-086/bootstrap.c').read_text()
    start = inner.index('    const char workspace087[] = ')
    end = inner.index('    commercial_system016();', start)
    assert inner[:start] + inner[end:] == original
    assert 'O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0644' in inner[start:end]
    assert 'upper/etc/hw_launcher_default_workspace.json' in inner[start:end]
    workspace = (folder / 'workspace.json').read_bytes()
    assert hashlib.sha256(workspace).hexdigest() == record['workspace_sha256']
    config = json.loads(workspace)
    assert config['layoutDescription'] == json.loads((ROOT / 'reports/commercial-dock-flow-audit-086/layoutInfo.json').read_text())['layoutDescription']
    assert len(config['layoutInfo']) == 1
    app = config['layoutInfo'][0]
    assert (app['bundleName'], app['moduleName'], app['abilityName'], app['typeId'], app['container']) == (
        'com.huawei.hmos.browser', 'entry', 'MainAbility', 0, -101)
    native = (ROOT / 'reports/commercial61-native-086/runtime-evidence/raw/interactive-hilog030.log').read_text(errors='replace')
    assert 'getCombIcon cacheKey com.huawei.hmos.browser#entryMainAbility0' in native
    assert 'MemoryCache --> setIconResource cacheKey com.huawei.hmos.browser#entryMainAbility0' in native
    outer = (BUILD / 'commercial61-native-087/init.c').read_text()
    assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD' in outer
    assert record['runtime_bootstrap_sha256'] in outer
    assert record['runtime_bootstrap_source'] in outer
    assert 'MS_RDONLY|MS_NODEV|MS_NOSUID|MS_NOEXEC, "noload"' in outer
    assert 'if(probe("workspace-bootstrap-load087",load087,8))okay=0' in outer
    assert outer.index('workspace-bootstrap-load087') < outer.index('char memory010[8192]')
    assert '"/network086-control", pid,' in outer
    assert 'force-stop' not in inner and 'force-stop' not in outer
    assert old['native-target/samgr_standard005.cfg'] == new['native-target/samgr_standard005.cfg']
    assert old['native-target/commercial-desktop077.sh'] == new['native-target/commercial-desktop077.sh']
    result = dict(exact_init_only_archive_delta=True, original_images_and_hap_unchanged=True,
                  unchanged_bootstrap_except_external_workspace=True, installed_browser_evidence_checked=True,
                  original_layout_dimensions_preserved=True, no_fake_bundle_or_provisioning=True,
                  runtime_sidecar_hash_guarded_source_and_destination=True, original_namespace_isolation_preserved=True,
                  original_network_helpers_and_credentials_unchanged=True, unchanged_service_identity_permissions=True,
                  original_ui_layout_attempt_unchanged=True, ram_only_product_config=True)
    (folder / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
    workflow = runpy.run_path(str(ROOT / 'next-experiment/commercial-workflow-087.py'))['source087']
    for name in ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return'):
        compile(workflow(name), '<workflow087>', 'exec')
    overlay = json.loads((folder / 'overlay-result.json').read_text())
    assert overlay['members'] == ['init'] and overlay['bytes'] < 400000
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
