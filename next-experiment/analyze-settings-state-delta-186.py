'''Compare supplied preinstalled records with the adaptation's seed policy.'''
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-ed213a0')
BUNDLE = 'com.huawei.hmos.settings'


def database_summary(database):
    installed, preinstalled, versions, paths = False, False, set(), set()
    for table in database['tables']:
        for match in table['settings_matches']:
            for record in match['records']:
                fields = record['fields']
                if fields.get('bundleName') != BUNDLE:
                    continue
                installed |= table['name'] == 'installed_bundle'
                preinstalled |= table['name'] == 'preinstalled_bundle'
                if 'versionCode' in fields:
                    versions.add(fields['versionCode'])
                for key in ['codePath', 'hapPath']:
                    if fields.get(key):
                        paths.add(fields[key])
    return dict(path=database['path'], source_sha256=database['sha256'],
                installed_record_observed=installed, preinstalled_record_observed=preinstalled,
                version_codes=sorted(versions), code_paths=sorted(paths),
                source_journal_version_hex=database['source_journal_version_hex'],
                memory_only_journal_header_normalized=database['memory_only_journal_header_normalized'],
                signature_validity_proven_by_records=False)


if __name__ == '__main__':
    folder = ROOT / 'reports/settings-state-delta-186'
    assert not folder.exists(), 'immutable result already exists'
    inputs = {}

    def read(path):
        data = path.read_bytes()
        inputs[str(path)] = hashlib.sha256(data).hexdigest()
        return data

    original = json.loads(read(ROOT / 'reports/settings-seed-db-185/result.json'))
    inventory = json.loads(read(ROOT / 'reports/settings-seed-bms-184/result.json'))
    latest = json.loads(read(ROOT / 'reports/commercial61-native-173/settings-usb-analysis.json'))
    install = json.loads(read(ROOT / 'reports/settings-diagnostics-155/result.json'))
    populate = read(REFERENCE / 'ports/tools/populate-rootfs.sh').decode()
    seed_source = read(ROOT / 'next-experiment/prepare-oobe-seed-123-remote.py').decode()
    assert 'state-seed.tar.zst' in populate and '--strip-components=2' in populate
    assert 'for name in (\'settingsdata.db\', \'settingsdata_slave.db\'):' in seed_source
    assert 'bmsdb' not in seed_source and 'bundle_manager_service' not in seed_source
    databases = [database_summary(row) for row in original['selected_files']]
    assert len(databases) == 2
    assert all(row['installed_record_observed'] and row['preinstalled_record_observed']
               and 600000412 in row['version_codes'] for row in databases)
    assert latest['live_settings_bundle_absent_user100']
    assert any(row['signing_block_missing'] and row['signature_error_8519742']
               for row in install['settings_install_failures'])
    result = dict(input_sha256=inputs, supplied_seed_databases=databases,
                  original_seed_hap_entry_count=len(inventory['all_regular_hap_entries']),
                  original_seed_settings_hap_entry_count=sum(
                      'settings' in row['path'].lower() for row in inventory['all_regular_hap_entries']),
                  harmony_mac_source_stages_original_state_seed=True,
                  adaptation_seed_source_explicitly_copies_bms_databases=False,
                  adaptation_seed_source_copies_only_settingsdata_databases=True,
                  latest_native173_settings_absent_user100=True,
                  prior_native153_signature_rejection=True,
                  state_migration_difference_is_relevant_hypothesis=True,
                  state_migration_difference_proven_sole_cause=False,
                  source_installed_record_is_not_signature_verification=True,
                  coherent_supplied_state_recovery_not_yet_tested=True,
                  target_modified=False, active_data_overwritten=False,
                  signature_checks_changed=False, usb_work_paused=True,
                  settings_repair_verified=False)
    folder.mkdir()
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(dict(databases=databases, source_hap_count=result['original_seed_hap_entry_count'],
                         settings_repair_verified=False), indent=2))
