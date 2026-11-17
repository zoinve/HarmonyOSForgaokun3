'''Classify source app-token device IDs without exporting identities or tokens.'''
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
API = runpy.run_path(str(Path(__file__).with_name('audit-settings-state-coherence-188.py')))


def classify(values):
    counts = dict(null=0, empty=0, zero=0, nonempty_nonzero=0)
    for value in values:
        if value is None:
            counts['null'] += 1
        elif value == '' or value == b'':
            counts['empty'] += 1
        elif value == 0 or value == '0' or value == b'0':
            counts['zero'] += 1
        else:
            counts['nonempty_nonzero'] += 1
    return counts


if __name__ == '__main__':
    folder = ROOT / 'reports/settings-state-deviceids-193'
    assert not folder.exists(), 'immutable result already exists'
    candidate_data = (ROOT / 'reports/settings-data-candidate-191-r2/result.json').read_bytes()
    candidate = json.loads(candidate_data)
    assert candidate['candidate_unmounted']
    image = Path(candidate['candidate_path'])
    assert not subprocess.check_output(['losetup', '-j', str(image)]).strip()
    relative = 'service/el1/public/access_token/access_token.db'
    original = json.loads((ROOT / 'reports/settings-preinstall-state-189/result.json').read_text())
    expected = next(row['sha256'] for row in original['members'] if row['path'] == relative)
    data = subprocess.run(['debugfs', '-R', 'cat /' + relative, str(image)],
                          capture_output=True, check=True).stdout
    assert hashlib.sha256(data).hexdigest() == expected
    connection = API['memory_database'](data)
    tables = []
    try:
        for (table,) in connection.execute('SELECT name FROM sqlite_master WHERE type=?', ('table',)):
            assert re.fullmatch(r'[A-Za-z0-9_]+', table)
            columns = [row[1] for row in connection.execute('PRAGMA table_info(' + table + ')')]
            for column in columns:
                if column.replace('_', '').lower() != 'deviceid':
                    continue
                assert re.fullmatch(r'[A-Za-z0-9_]+', column)
                values = [row[0] for row in connection.execute('SELECT ' + column + ' FROM ' + table)]
                tables.append(dict(table=table, column=column, counts=classify(values)))
        settings = classify(row[0] for row in connection.execute(
            'SELECT device_id FROM hap_token_info_table WHERE bundle_name=? AND user_id=?',
            ('com.huawei.hmos.settings', 100)))
    finally:
        connection.close()
    result = dict(candidate_report_sha256=hashlib.sha256(candidate_data).hexdigest(),
                  original_token_database_sha256=expected, source_token_database_bytes_unchanged=True,
                  device_id_columns=tables, settings_user100_device_id_counts=settings,
                  nonempty_nonzero_source_device_ids_observed=any(
                      row['counts']['nonempty_nonzero'] for row in tables),
                  raw_device_ids_or_tokens_exported=False, image_mounted_or_written=False,
                  target_modified=False, candidate_promoted_or_booted=False,
                  classification_does_not_verify_real_hardware_identity=True)
    folder.mkdir()
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
