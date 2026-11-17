'''Read actual SettingsData provider ownership from the supplied BMS state.'''
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
API = runpy.run_path(str(Path(__file__).with_name('audit-settings-state-coherence-188.py')))


if __name__ == '__main__':
    folder = ROOT / 'reports/settingsdata-owner-192'
    assert not folder.exists(), 'immutable result already exists'
    image = Path('/home/zoinve/harmony-virgl-883/settings-data-candidate-191-r1/data.ext4')
    path = '/service/el1/public/bms/bundle_manager_service/bmsdb.db'
    data = subprocess.run(['debugfs', '-R', 'cat ' + path, str(image)],
                          capture_output=True, check=True).stdout
    original = json.loads((ROOT / 'reports/settings-preinstall-state-189/result.json').read_text())
    expected = next(row['sha256'] for row in original['members'] if row['path'] == path.lstrip('/'))
    assert hashlib.sha256(data).hexdigest() == expected
    connection = API['memory_database'](data)
    rows = []
    try:
        for key, value in connection.execute('SELECT KEY, VALUE FROM installed_bundle'):
            if not re.fullmatch(r'com\.ohos\.settingsdata(?:_\d+)?', key):
                continue
            users = []
            singleton = []
            for node in API['dicts'](json.loads(value)):
                user = node.get('bundleUserInfo')
                if isinstance(user, dict):
                    users.append(dict(user_id=user.get('userId'), uid=node.get('uid')))
                if isinstance(node.get('singleton'), bool):
                    singleton.append(node['singleton'])
            rows.append(dict(bundle_key=key, users=users, singleton_flags=singleton))
    finally:
        connection.close()
    assert rows
    result = dict(source_database_sha256=expected, source_database_bytes_unmodified=True,
                  settingsdata_records=rows, existing_database_directory_user_component=0,
                  candidate_mount_or_write_performed=False, raw_tokens_exported=False,
                  target_modified=False, current_data165_modified=False)
    folder.mkdir()
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
