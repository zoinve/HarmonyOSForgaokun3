'''Identify the upstream fixed storage marker without rewriting permissions.'''
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
UPSTREAM = BUILD / 'access-token-reference-196'
COMMIT = '53287abcc13b418c091154fdb629c37dcfa34ce6'
API = runpy.run_path(str(Path(__file__).with_name('audit-settings-state-coherence-188.py')))


def git_output(*args, text=False):
    command = ['git', '-C', str(UPSTREAM), *args]
    if os.geteuid() == 0:
        command = ['runuser', '-u', 'zoinve', '--', *command]
    return subprocess.check_output(command, text=text)


if __name__ == '__main__':
    folder = ROOT / 'reports/permission-device-marker-196'
    assert not folder.exists(), 'immutable result already exists'
    assert git_output('rev-parse', 'HEAD', text=True).strip() == COMMIT
    paths = ['services/accesstokenmanager/main/cpp/src/database/data_translator.cpp',
             'services/accesstokenmanager/main/cpp/src/permission/hap_token_info_inner.cpp']
    source = [git_output('show', 'HEAD:' + path) for path in paths]
    quote = chr(34)
    marker = 'PHONE-001'
    expected = 'outGenericValues.Put(TokenFiledConst::FIELD_DEVICE_ID, ' + quote + marker + quote + ');'
    assert expected in source[0].decode()
    expected = 'genericValues.Put(TokenFiledConst::FIELD_DEVICE_ID, ' + quote + '0' + quote + ');'
    assert expected in source[1].decode()
    candidate = json.loads((ROOT / 'reports/settings-data-candidate-191-r2/result.json').read_text())
    image = Path(candidate['candidate_path'])
    assert not subprocess.check_output(['losetup', '-j', str(image)]).strip()
    data = subprocess.run(['debugfs', '-R', 'cat /service/el1/public/access_token/access_token.db', str(image)],
                          capture_output=True, check=True).stdout
    prior_data = (ROOT / 'reports/settings-state-deviceids-193/result.json').read_bytes()
    assert hashlib.sha256(data).hexdigest() == json.loads(prior_data)['original_token_database_sha256']
    connection = API['memory_database'](data)
    try:
        values = [row[0] for row in connection.execute('SELECT device_id FROM permission_state_table')]
        local = connection.execute('SELECT count(*) FROM hap_token_info_table WHERE device_id=?', ('0',)).fetchone()[0]
        total_haps = connection.execute('SELECT count(*) FROM hap_token_info_table').fetchone()[0]
    finally:
        connection.close()
    reader = runpy.run_path(str(Path(__file__).with_name('audit-board-driver-contracts-126.py')))
    original_image = reader['IMAGES'] / 'p111-system.kr990-ext4-v1.img'
    libraries = []
    for name in reader['names'](original_image, '/system/lib64'):
        if 'accesstoken' not in name and 'access_token' not in name:
            continue
        payload = reader['read'](original_image, 'cat /system/lib64/' + name)
        if payload.startswith(b'\x7fELF') and marker.encode() + b'\0' in payload:
            libraries.append(dict(path='/system/lib64/' + name, bytes=len(payload),
                                  sha256=hashlib.sha256(payload).hexdigest(), public_marker_present=True))
    assert values and all(value == marker for value in values)
    assert local == total_haps and total_haps > 0
    assert libraries, 'upstream behavior alone is insufficient without source-binary corroboration'
    result = dict(upstream_repository='openharmony/security_access_token',
                  initial_root_git_query_refused_ownership=True,
                  git_read_as_existing_repository_owner=True, global_git_security_config_changed=False,
                  upstream_release_branch='OpenHarmony-6.0-Release', upstream_commit=COMMIT,
                  upstream_files=[dict(path=path, sha256=hashlib.sha256(payload).hexdigest())
                                  for path, payload in zip(paths, source)],
                  upstream_permission_storage_constant=marker,
                  supplied_permission_rows=len(values), rows_matching_public_constant=len(values),
                  unmatched_permission_rows=0, local_hap_token_rows_with_zero_device_id=local,
                  total_hap_token_rows=total_haps, commercial_libraries_with_same_marker=libraries,
                  evidence_supports_fixed_schema_marker_not_unique_hardware_id=True,
                  commercial_binary_literal_not_complete_codepath_verification=True,
                  upstream_release_not_asserted_byte_identical_to_commercial_build=True,
                  raw_nonconstant_device_ids_or_tokens_exported=False,
                  source_token_database_unchanged=True, device_identity_rewritten=False,
                  target_modified=False, candidate_installed_or_booted=False,
                  real_hardware_identity_or_settings_ui_verified=False,
                  initial_classification_reference_sha256=hashlib.sha256(prior_data).hexdigest())
    folder.mkdir()
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
