'''Compare supplied BMS/token/resource state without exporting token values.'''
import hashlib
import io
import json
from pathlib import Path
import re
import runpy
import sqlite3
import zipfile

ROOT = Path(__file__).resolve().parents[1]
API = runpy.run_path(str(Path(__file__).with_name('audit-settings-seed-183.py')))
BUNDLE = 'com.huawei.hmos.settings'
STATE = './.hmos-data/'
BMS = STATE + 'service/el1/public/bms/bundle_manager_service/'
TOKENS = STATE + 'service/el1/public/access_token/'
PUBLIC = STATE + 'app/el1/bundle/public/' + BUNDLE + '/'
CODE = {
    PUBLIC + 'libs/arm64/libc++_shared.so': 'libs/arm64-v8a/libc++_shared.so',
    PUBLIC + 'libs/arm64/libnative.so': 'libs/arm64-v8a/libnative.so',
    PUBLIC + 'pc_settings/resources.index': 'resources.index',
}
DATABASES = {BMS + 'bmsdb.db', BMS + 'bmsdb_slave.db',
             TOKENS + 'access_token.db', TOKENS + 'access_token_slave.db'}


def dicts(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from dicts(child)


def bms_links(connection):
    tokens = set()
    rows = 0
    user100 = 0
    for key, value in connection.execute('SELECT KEY, VALUE FROM installed_bundle'):
        if not isinstance(key, str) or not re.fullmatch(re.escape(BUNDLE) + r'(?:_\d+)?', key):
            continue
        rows += 1
        for node in dicts(json.loads(value)):
            user = node.get('bundleUserInfo')
            if not isinstance(user, dict) or user.get('userId') != 100:
                continue
            user100 += 1
            token = node.get('accessTokenId')
            if isinstance(token, int) and not isinstance(token, bool) and token > 0:
                tokens.add(token)
    return dict(bundle_rows=rows, user100_records=user100, private_tokens=tokens)


def token_links(connection):
    schemas = []
    tokens = set()
    matching_rows = 0
    normalize = lambda name: name.replace('_', '').lower()
    for (table,) in connection.execute('SELECT name FROM sqlite_master WHERE type=?', ('table',)):
        assert re.fullmatch(r'[A-Za-z0-9_]+', table)
        columns = [row[1] for row in connection.execute('PRAGMA table_info(' + table + ')')]
        schemas.append(dict(table=table, columns=columns))
        keys = [normalize(name) for name in columns]
        if not all(key in keys for key in ['bundlename', 'userid', 'tokenid']):
            continue
        for row in connection.execute('SELECT * FROM ' + table):
            if row[keys.index('bundlename')] != BUNDLE or row[keys.index('userid')] != 100:
                continue
            matching_rows += 1
            token = row[keys.index('tokenid')]
            if isinstance(token, int) and not isinstance(token, bool) and token > 0:
                tokens.add(token)
    return dict(schemas=schemas, user100_records=matching_rows, private_tokens=tokens)


def summarize_links(bms, token):
    return dict(bms_bundle_rows=bms['bundle_rows'], bms_user100_records=bms['user100_records'],
                token_user100_records=token['user100_records'],
                bms_token_reference_count=len(bms['private_tokens']),
                hap_token_reference_count=len(token['private_tokens']),
                unique_user100_token_matches=(len(bms['private_tokens']) == 1
                    and bms['private_tokens'] == token['private_tokens']),
                raw_token_values_exported=False,
                token_match_is_not_signature_verification=True)


def memory_database(data):
    assert data.startswith(b'SQLite format 3\0')
    assert data[18:20] in [b'\x01\x01', b'\x02\x02']
    memory = data[:18] + b'\x01\x01' + data[20:]
    connection = sqlite3.connect(':memory:')
    try:
        connection.deserialize(memory)
        connection.execute('PRAGMA query_only=ON')
        assert connection.execute('PRAGMA integrity_check').fetchall() == [('ok',)]
    except BaseException:
        connection.close()
        raise
    return connection


if __name__ == '__main__':
    folder = ROOT / 'reports/settings-state-coherence-188'
    assert not folder.exists(), 'immutable result already exists'
    inventory_data = [(ROOT / path).read_bytes() for path in [
        'reports/settings-seed-bms-184/result.json', 'reports/settings-state-inventory-187/result.json']]
    entries = json.loads(inventory_data[0])['bms_entries'] + json.loads(inventory_data[1])['entries']
    for database in DATABASES:
        assert any(row['path'] == database and row['file_type'] == '0o100000' for row in entries)
        assert not any(row['path'] == database + '-wal' and row['bytes'] != 0 for row in entries)
    captured = {}

    def inspect(data):
        digest = hashlib.sha256(data).hexdigest()
        captured[digest] = data
        return dict(bytes=len(data), sha256=digest, raw_content_exported=False)

    result = API['scan_archive'](select=lambda name: name in DATABASES or name in CODE, inspect=inspect)
    assert len(result['selected_files']) == len(DATABASES) + len(CODE)
    members = {row['path']: captured[row['sha256']] for row in result['selected_files']}
    connections = {}
    try:
        for name in DATABASES:
            connections[name] = memory_database(members[name])
        comparisons = []
        for bms_name, token_name in [('bmsdb.db', 'access_token.db'),
                                     ('bmsdb_slave.db', 'access_token_slave.db')]:
            bms = bms_links(connections[BMS + bms_name])
            token = token_links(connections[TOKENS + token_name])
            comparisons.append(dict(bms_database=bms_name, token_database=token_name,
                                    **summarize_links(bms, token)))
        schemas = token_links(connections[TOKENS + 'access_token.db'])['schemas']
    finally:
        for connection in connections.values():
            connection.close()
    hap = (ROOT / 'reports/commercial-bundle-inputs-audit-066/Settings.hap').read_bytes()
    assert hashlib.sha256(hap).hexdigest() == '299cfd91df8456b6f46d6fe4c3056e38f9d7f2b04e66466e16fa3d95768bed5c'
    files = []
    with zipfile.ZipFile(io.BytesIO(hap)) as archive:
        for path, member in CODE.items():
            payload = archive.read(member)
            files.append(dict(seed_path=path, hap_member=member,
                              seed_sha256=hashlib.sha256(members[path]).hexdigest(),
                              hap_member_sha256=hashlib.sha256(payload).hexdigest(),
                              byte_identical=members[path] == payload))
    result.update(inventory_sha256=[hashlib.sha256(data).hexdigest() for data in inventory_data],
                  initial_scan_failed_on_wrong_hap_abi_directory=True,
                  source_wals_empty_or_absent=True, database_integrity_checks_pass=True,
                  token_schemas=schemas, token_comparisons=comparisons, code_comparisons=files,
                  memory_only_journal_header_normalization=True, active_data_modified=False,
                  source_state_restored=False, original_signature_checks_changed=False,
                  settings_installation_or_ui_verified=False,
                  content_read_scope='Four source databases and three Settings public code files, memory only')
    folder.mkdir()
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(dict(token_comparisons=comparisons, code_comparisons=files), indent=2))
