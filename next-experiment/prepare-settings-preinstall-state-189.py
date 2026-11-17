'''Stage a private original-install-state archive, never applying it to a device.'''
import csv
import ctypes
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import runpy
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
API = runpy.run_path(str(Path(__file__).with_name('audit-settings-seed-183.py')))
ALLOWED = ('app/el1/bundle', 'service/el0/access_token',
           'service/el1/public/access_token', 'service/el1/public/bms',
           'service/el1/public/database/bundle_manager_service')


def relative_selected(name):
    if not name.startswith('./.hmos-data/'):
        return None
    relative = name[len('./.hmos-data/'):].rstrip('/')
    if not relative or '\\' in relative or '\r' in relative or '\n' in relative:
        return None
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or '.' in path.parts or str(path) != relative:
        return None
    if any(relative == prefix or relative.startswith(prefix + '/')
           or prefix.startswith(relative + '/') for prefix in ALLOWED):
        return relative
    return None


def bind(lib, name, result, args):
    function = getattr(lib, name)
    function.restype, function.argtypes = result, args
    return function


def build_archive(path):
    writer = None
    library = None
    output = path.open('xb')
    os.fchmod(output.fileno(), 0o600)
    rows = []
    seen = set()
    pointer = ctypes.c_void_p

    def consume(name, size, kind, lib, reader, entry):
        nonlocal writer, library
        relative = relative_selected(name)
        if relative is None:
            return
        assert kind in [0o100000, 0o40000], 'unsupported original archive entry type'
        assert relative not in seen, 'duplicate selected archive path'
        seen.add(relative)
        if writer is None:
            library = lib
            signatures = {
                'archive_write_new': (pointer, []),
                'archive_write_set_format_pax': (ctypes.c_int, [pointer]),
                'archive_write_add_filter_gzip': (ctypes.c_int, [pointer]),
                'archive_write_open_fd': (ctypes.c_int, [pointer, ctypes.c_int]),
                'archive_write_header': (ctypes.c_int, [pointer, pointer]),
                'archive_write_data': (ctypes.c_ssize_t, [pointer, pointer, ctypes.c_size_t]),
                'archive_write_finish_entry': (ctypes.c_int, [pointer]),
                'archive_write_close': (ctypes.c_int, [pointer]),
                'archive_write_free': (ctypes.c_int, [pointer]),
                'archive_entry_clone': (pointer, [pointer]),
                'archive_entry_free': (None, [pointer]),
                'archive_entry_set_pathname': (None, [pointer, ctypes.c_char_p]),
                'archive_entry_hardlink': (ctypes.c_char_p, [pointer]),
                'archive_entry_uid': (ctypes.c_longlong, [pointer]),
                'archive_entry_gid': (ctypes.c_longlong, [pointer]),
                'archive_entry_perm': (ctypes.c_uint, [pointer]),
            }
            for function, (result, args) in signatures.items():
                bind(lib, function, result, args)
            writer = lib.archive_write_new()
            assert writer
            assert lib.archive_write_set_format_pax(writer) == 0
            assert lib.archive_write_add_filter_gzip(writer) == 0
            assert lib.archive_write_open_fd(writer, output.fileno()) == 0
        assert not lib.archive_entry_hardlink(entry), 'hardlinks require an explicit source plan'
        clone = lib.archive_entry_clone(entry)
        assert clone
        digest = hashlib.sha256()
        try:
            lib.archive_entry_set_pathname(clone, relative.encode())
            assert lib.archive_write_header(writer, clone) == 0, lib.archive_error_string(writer)
            if kind == 0o100000:
                buffer = ctypes.create_string_buffer(1024 * 1024)
                total = 0
                while True:
                    length = lib.archive_read_data(reader, buffer, len(buffer))
                    assert length >= 0
                    if not length:
                        break
                    digest.update(buffer.raw[:length])
                    assert lib.archive_write_data(writer, buffer, length) == length
                    total += length
                assert total == size
            assert lib.archive_write_finish_entry(writer) == 0
            rows.append(dict(path=relative, bytes=size, kind=kind,
                             uid=lib.archive_entry_uid(entry), gid=lib.archive_entry_gid(entry),
                             mode=lib.archive_entry_perm(entry),
                             sha256=digest.hexdigest() if kind == 0o100000 else None))
        finally:
            lib.archive_entry_free(clone)

    try:
        scan = API['scan_archive'](select=lambda name: False, consume=consume)
        assert writer and rows
        assert library.archive_write_close(writer) == 0
        output.flush()
        os.fsync(output.fileno())
    finally:
        if writer:
            library.archive_write_free(writer)
        output.close()
    return scan['entries_inspected'], rows


def verify_archive(path, expected):
    expected = {row['path']: row for row in expected}
    seen = set()
    with tarfile.open(path, 'r|gz') as archive:
        for member in archive:
            assert member.name in expected and member.name not in seen
            seen.add(member.name)
            row = expected[member.name]
            assert (member.uid, member.gid, member.mode, member.size) == (
                row['uid'], row['gid'], row['mode'], row['bytes'])
            assert (member.isdir() and row['kind'] == 0o40000) or (member.isfile() and row['kind'] == 0o100000)
            if member.isfile():
                digest = hashlib.sha256()
                with archive.extractfile(member) as stream:
                    while block := stream.read(1024 * 1024):
                        digest.update(block)
                assert digest.hexdigest() == row['sha256']
    assert seen == expected.keys()


if __name__ == '__main__':
    work = BUILD / 'settings-preinstall-state-189'
    report = ROOT / 'reports/settings-preinstall-state-189'
    assert not work.exists() and not report.exists(), 'preserve numbered outputs'
    coherence_data = (ROOT / 'reports/settings-state-coherence-188/result.json').read_bytes()
    coherence = json.loads(coherence_data)
    assert all(row['unique_user100_token_matches'] for row in coherence['token_comparisons'])
    assert all(row['byte_identical'] for row in coherence['code_comparisons'])
    work.mkdir(mode=0o700)
    report.mkdir()
    archive = work / 'preinstall-state.tar.gz'
    count, rows = build_archive(archive)
    verify_archive(archive, rows)
    tools = BUILD / 'commercial61-tools-001/root'
    env = dict(os.environ, LD_LIBRARY_PATH=str(tools / 'usr/lib/x86_64-linux-gnu'))
    data = subprocess.check_output([str(tools / 'usr/bin/unsquashfs'), '-cat',
        str(BUILD / 'commercial61-iso-001/payload.squashfs'), 'state-labels.tsv'], env=env)
    source_labels = list(csv.DictReader(io.StringIO(data.decode()), delimiter='\t'))
    selected = {row['path'] for row in rows}
    labels = []
    for row in source_labels:
        relative = relative_selected('./' + row['path'])
        if relative in selected:
            labels.append(dict(path=relative, selinux=row['selinux']))
    label_paths = {row['path'] for row in labels}
    with (work / 'preinstall-labels.tsv').open('x', newline='') as stream:
        os.fchmod(stream.fileno(), 0o600)
        writer = csv.DictWriter(stream, fieldnames=['path', 'selinux'], delimiter='\t')
        writer.writeheader()
        writer.writerows(labels)
    with archive.open('rb') as stream:
        archive_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    result = dict(source_entries_inspected=count, source_coherence_sha256=hashlib.sha256(coherence_data).hexdigest(),
                  archive=str(archive), archive_bytes=archive.stat().st_size, archive_sha256=archive_sha,
                  members=rows, member_count=len(rows), original_payload_bytes=sum(row['bytes'] for row in rows),
                  archive_reread_all_hashes_and_owners_verified=True,
                  label_count=len(labels), all_member_labels_present=selected <= label_paths,
                  members_without_source_label=sorted(selected - label_paths),
                  labels_sha256=hashlib.sha256((work / 'preinstall-labels.tsv').read_bytes()).hexdigest(),
                  explicit_install_state_allowlist=list(ALLOWED), symbolic_or_hard_links_allowed=False,
                  account_activation_device_identity_network_auth_state_included=False,
                  native_service_permission_map_preserved_from_source=True,
                  target_modified=False, active_persistent_data_modified=False,
                  original_images_modified=False, original_signature_checks_changed=False,
                  candidate_data_filesystem_prepared=False, settings_ui_verified=False,
                  private_payload_not_copied_to_reports=True, usb_work_paused=True)
    with (report / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({key: value for key, value in result.items() if key != 'members'}, indent=2))
