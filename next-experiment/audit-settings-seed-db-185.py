'''Query original factory BMS databases in memory, exporting no token values.'''
import hashlib
import json
from pathlib import Path
import re
import runpy
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = runpy.run_path(str(Path(__file__).with_name('audit-settings-seed-183.py')))
RECORDS = runpy.run_path(str(Path(__file__).with_name('audit-settings-seed-bms-184.py')))


def selected_database(name):
    return name in {
        './.hmos-data/service/el1/public/bms/bundle_manager_service/bmsdb.db',
        './.hmos-data/service/el1/public/bms/bundle_manager_service/bmsdb_slave.db'}


def inspect_database(data, empty_wal_verified=False):
    result = dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                  sqlite_header=data.startswith(b'SQLite format 3\0'), tables=[],
                  database_restored=False, raw_values_exported=False)
    if not result['sqlite_header']:
        return result
    result['source_journal_version_hex'] = data[18:20].hex()
    result['memory_only_journal_header_normalized'] = False
    query_data = data
    if data[18:20] == b'\x02\x02':
        assert empty_wal_verified, 'must verify no WAL transactions before memory-only normalization'
        # sqlite3_deserialize documents this in-memory WAL-header workaround.
        query_data = data[:18] + b'\x01\x01' + data[20:]
        result['memory_only_journal_header_normalized'] = True
    connection = sqlite3.connect(':memory:')
    try:
        connection.deserialize(query_data)
        connection.execute('PRAGMA query_only=ON')
        tables = connection.execute('SELECT name FROM sqlite_master WHERE type=?', ('table',)).fetchall()
        for (name,) in tables:
            assert re.fullmatch(r'[A-Za-z0-9_]+', name), 'unexpected table identifier'
            columns = [row[1] for row in connection.execute('PRAGMA table_info(' + name + ')')]
            table = dict(name=name, columns=columns, row_count=0, settings_matches=[])
            for row in connection.execute('SELECT * FROM ' + name):
                table['row_count'] += 1
                key_match = any(value == RECORDS['BUNDLE'] for value in row)
                for column, value in zip(columns, row):
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8')
                        except UnicodeError:
                            continue
                    if not isinstance(value, str) or (not key_match and RECORDS['BUNDLE'] not in value):
                        continue
                    try:
                        records = RECORDS['summarize_json'](value.encode())['settings_records']
                    except (ValueError, TypeError):
                        continue
                    if records:
                        table['settings_matches'].append(dict(column=column, records=records))
            result['tables'].append(table)
    finally:
        connection.close()
    return result


if __name__ == '__main__':
    folder = ROOT / 'reports/settings-seed-db-185'
    assert not folder.exists(), 'immutable result already exists'
    inventory_path = ROOT / 'reports/settings-seed-bms-184/result.json'
    inventory_data = inventory_path.read_bytes()
    inventory = json.loads(inventory_data)
    entries = inventory['bms_entries']
    prefix = './.hmos-data/service/el1/public/bms/bundle_manager_service/'
    main_wal = [row for row in entries if row['path'] == prefix + 'bmsdb.db-wal']
    assert len(main_wal) == 1 and main_wal[0]['bytes'] == 0
    assert not any(row['path'] == prefix + 'bmsdb_slave.db-wal' and row['bytes'] for row in entries)
    result = ARCHIVE['scan_archive'](select=selected_database,
        inspect=lambda data: inspect_database(data, empty_wal_verified=True))
    result.update(content_read_scope='Two original BMS database members, memory-only SQLite queries',
                  wal_inventory_sha256=hashlib.sha256(inventory_data).hexdigest(),
                  source_main_wal_empty=True, source_slave_nonempty_wal_present=False,
                  initial_unmodified_deserialize_failed='SQLITE_CANTOPEN on WAL-mode input',
                  factory_records_not_assumed_valid_for_current_package=True,
                  signature_checks_changed=False, settings_repair_verified=False)
    assert len(result['selected_files']) == 2
    folder.mkdir()
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
