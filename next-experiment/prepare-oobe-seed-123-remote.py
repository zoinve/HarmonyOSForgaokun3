"""Executed on target Ubuntu with generated, hash-pinned pristine inputs."""
from pathlib import Path
from contextlib import closing
import base64
import gzip
import hashlib
import json
import os
import runpy
import sqlite3
import stat
import subprocess


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def ancestors(relative):
    return [p for p in reversed(relative.parents) if p != Path('.')] + [relative]


def content_without_setup(db):
    result = {}
    for (table,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        quoted = '"' + table.replace('"', '""') + '"'
        columns = [row[1] for row in db.execute('PRAGMA table_info(' + quoted + ')')]
        rows = []
        for row in db.execute('SELECT * FROM ' + quoted):
            if table in ('SETTINGSDATA', 'USER_SETTINGSDATA_SECURE_100'):
                key = row[columns.index('KEYWORD')]
                if (table, key) in (('SETTINGSDATA', 'device_provisioned'),
                                    ('USER_SETTINGSDATA_SECURE_100', 'user_setup_complete')):
                    continue
            if table == 'sqlite_sequence' and row[0] in ('SETTINGSDATA', 'USER_SETTINGSDATA_SECURE_100'):
                continue
            rows.append(repr(tuple(row)).encode())
        encoded = b''.join(len(row).to_bytes(8, 'big') + row for row in sorted(rows))
        result[table] = dict(rows=len(rows), sha256=hashlib.sha256(encoded).hexdigest())
    return result


def copy_metadata(source, destination):
    state = source.stat()
    os.chown(destination, state.st_uid, state.st_gid)
    os.chmod(destination, stat.S_IMODE(state.st_mode))
    for name in os.listxattr(source):
        os.setxattr(destination, name, os.getxattr(source, name))
    os.utime(destination, ns=(state.st_atime_ns, state.st_mtime_ns))
    actual = destination.stat()
    assert (actual.st_uid, actual.st_gid, stat.S_IMODE(actual.st_mode)) == (
        state.st_uid, state.st_gid, stat.S_IMODE(state.st_mode))
    assert {name: os.getxattr(destination, name) for name in os.listxattr(destination)} == {
        name: os.getxattr(source, name) for name in os.listxattr(source)}


def main():
    root = Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/oobe-seed-123')
    inspection = Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/oobe-snapshot-inspection-122')
    assert os.geteuid() == 0 and not root.exists() and not root.is_symlink()
    assert not subprocess.run(['findmnt', '-rn', '--source', '/dev/nvme0n1p4'], capture_output=True).stdout.strip()
    previous = json.loads((inspection / 'inspection-result.json').read_text())
    assert previous['source_snapshot_sha256'] == EXPECTED_SNAPSHOT_SHA123
    assert len(previous['databases']) == 2 and all(d['integrity_check'] == 'ok' for d in previous['databases'])
    root.mkdir(mode=0o700)
    source_mount = root / 'source-clone-mount'
    seed_mount = root / 'seed-mount'
    source_mount.mkdir(mode=0o700)
    seed_mount.mkdir(mode=0o700)
    upstream = base64.b64decode(UPSTREAM_SOURCE_BASE64123)
    assert hashlib.sha256(upstream).hexdigest() == EXPECTED_UPSTREAM_SHA123
    (root / 'upstream-prepare.py').open('xb').write(upstream)
    prepare = runpy.run_path(str(root / 'upstream-prepare.py'))['prepare']
    pristine = gzip.decompress(base64.b64decode(PRISTINE_GZIP_BASE64123))
    assert len(pristine) == 536870912 and hashlib.sha256(pristine).hexdigest() == EXPECTED_PRISTINE_SHA123
    seed = root / 'seed.ext4'
    with seed.open('xb') as stream:
        # Preserve holes instead of allocating every empty ext4 block on Ubuntu.
        for at in range(0, len(pristine), 1024 * 1024):
            block = pristine[at:at + 1024 * 1024]
            if block.strip(b'\0'):
                stream.seek(at)
                stream.write(block)
        stream.truncate(len(pristine))
    del pristine
    assert digest(seed) == EXPECTED_PRISTINE_SHA123
    source = inspection / 'data-working.ext4'
    assert source.is_file() and not source.is_symlink() and source.stat().st_size == 8589934592
    mounted_source = mounted_seed = False
    result = dict(reference_commit='ed213a08817c642e9b455fb7d8f5271da41631eb',
        reference_prepare_sha256=EXPECTED_UPSTREAM_SHA123, source_snapshot_sha256=EXPECTED_SNAPSHOT_SHA123,
        pristine_seed_sha256=EXPECTED_PRISTINE_SHA123, raw_databases_exported=False,
        original_images_modified=False, commercial_activation_modified=False,
        only_local_first_run_settings_modified=True, sceneboard_cache_copied=False, databases=[])
    try:
        subprocess.run(['mount', '-t', 'ext4', '-o', 'loop,nodev,nosuid,noexec', str(source), str(source_mount)], check=True)
        mounted_source = True
        subprocess.run(['mount', '-t', 'ext4', '-o', 'loop,nodev,nosuid,noexec', str(seed), str(seed_mount)], check=True)
        mounted_seed = True
        relative = Path('app/el1/0/database/com.ohos.settingsdata/entry/rdb')
        original_directory = source_mount / relative
        target_directory = seed_mount / relative
        parents = ancestors(relative)
        # Explicitly reconstruct only the real ancestors of SettingsData's RDB directory.
        for parent in parents:
            original = source_mount / parent
            target = seed_mount / parent
            assert original.is_dir() and not original.is_symlink()
            if not target.exists():
                target.mkdir()
            assert target.is_dir() and not target.is_symlink()
            copy_metadata(original, target)
        assert target_directory.is_dir()
        for name in ('settingsdata.db', 'settingsdata_slave.db'):
            original = original_directory / name
            checkpointed = root / (name + '.checkpointed')
            prepared = root / (name + '.prepared')
            assert original.is_file() and not original.is_symlink()
            with closing(sqlite3.connect(original.as_uri() + '?mode=ro', uri=True)) as live:
                live.execute('PRAGMA query_only=ON')
                assert live.execute('PRAGMA integrity_check').fetchall() == [('ok',)]
                with closing(sqlite3.connect(checkpointed)) as offline:
                    live.backup(offline)
            assert all(not Path(str(checkpointed) + suffix).exists() for suffix in ('-wal', '-shm', '-journal'))
            with closing(sqlite3.connect(checkpointed.as_uri() + '?mode=ro&immutable=1', uri=True)) as before:
                schema = before.execute('SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name').fetchall()
                unrelated = content_without_setup(before)
                versions = [before.execute('PRAGMA ' + key).fetchone() for key in ('user_version', 'application_id')]
            change = prepare(checkpointed, prepared, 100)
            with closing(sqlite3.connect(prepared.as_uri() + '?mode=ro&immutable=1', uri=True)) as after:
                assert after.execute('SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name').fetchall() == schema
                assert content_without_setup(after) == unrelated
                assert [after.execute('PRAGMA ' + key).fetchone() for key in ('user_version', 'application_id')] == versions
                for table, key in [('SETTINGSDATA', 'device_provisioned'), ('USER_SETTINGSDATA_SECURE_100', 'user_setup_complete')]:
                    assert after.execute('SELECT VALUE FROM "' + table + '" WHERE KEYWORD=?', (key,)).fetchall() == [('1',)]
                    sequence = after.execute('SELECT seq FROM sqlite_sequence WHERE name=?', (table,)).fetchone()
                    maximum = after.execute('SELECT MAX(ID) FROM "' + table + '"').fetchone()[0]
                    assert sequence is not None and sequence[0] >= maximum
            target = target_directory / name
            assert not target.exists()
            with prepared.open('rb') as incoming, target.open('xb') as outgoing:
                while block := incoming.read(1024 * 1024):
                    outgoing.write(block)
                outgoing.flush()
                os.fsync(outgoing.fileno())
            copy_metadata(original, target)
            assert digest(target) == change['output_sha256']
            result['databases'].append(dict(name=name, changes=change['changes'], sha256=digest(target),
                uid=target.stat().st_uid, gid=target.stat().st_gid, mode=oct(stat.S_IMODE(target.stat().st_mode)),
                all_xattrs_preserved=True, schema_preserved=True, unrelated_rows_preserved=True,
                sidecars_in_original_snapshot_preserved=True, sqlite_backup_includes_committed_wal=True))
        assert sorted(p.name for p in target_directory.iterdir()) == ['settingsdata.db', 'settingsdata_slave.db']
        assert not (seed_mount / 'app/el1/0/base/com.ohos.sceneboard').exists()
        os.sync()
    finally:
        if mounted_seed:
            subprocess.run(['umount', str(seed_mount)], check=True)
        if mounted_source:
            subprocess.run(['umount', str(source_mount)], check=True)
    checked = subprocess.run(['e2fsck', '-fn', str(seed)], capture_output=True)
    (root / 'seed-e2fsck.stdout').open('xb').write(checked.stdout)
    (root / 'seed-e2fsck.stderr').open('xb').write(checked.stderr)
    assert checked.returncode == 0, checked.returncode
    os.chmod(seed, 0o600)
    result.update(seed_path=str(seed), seed_bytes=seed.stat().st_size, seed_sha256=digest(seed),
                  seed_e2fsck_status=0, target_boot_performed=False, desktop_verified=False)
    assert result['seed_bytes'] == 536870912
    (root / 'preparation-result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
