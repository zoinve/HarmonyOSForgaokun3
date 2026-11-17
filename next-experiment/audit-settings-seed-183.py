'''Search the original installer seed for Settings HAPs; never extract state.'''
import ctypes
import ctypes.util
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')


def selected_hap(name):
    path = PurePosixPath(name)
    return path.suffix.lower() == '.hap' and (
        'settings' in path.name.lower() or
        'com.huawei.hmos.settings' in path.parts or
        'com.huawei.hmos.pcsettings' in path.parts)


def inspect_hap(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        module = json.loads(archive.read('module.json')) if 'module.json' in archive.namelist() else {}
        tail = data[max(0, archive.start_dir - 32):archive.start_dir]
        app = module.get('app', {})
        return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                    bundle_name=app.get('bundleName'), version_name=app.get('versionName'),
                    central_directory_offset=archive.start_dir,
                    preceding_32_bytes_hex=tail.hex(),
                    hap_sign_marker_in_tail=b'<hap sign block>' in tail,
                    cryptographic_signature_verified=False)


def scan_archive(select=selected_hap, inspect=inspect_hap, observe=None, consume=None):
    lib = ctypes.CDLL(ctypes.util.find_library('archive'))
    pointer = ctypes.c_void_p
    signatures = {
        'archive_read_new': (pointer, []),
        'archive_read_support_filter_all': (ctypes.c_int, [pointer]),
        'archive_read_support_format_tar': (ctypes.c_int, [pointer]),
        'archive_read_open_fd': (ctypes.c_int, [pointer, ctypes.c_int, ctypes.c_size_t]),
        'archive_read_next_header': (ctypes.c_int, [pointer, ctypes.POINTER(pointer)]),
        'archive_entry_pathname': (ctypes.c_char_p, [pointer]),
        'archive_entry_size': (ctypes.c_longlong, [pointer]),
        'archive_entry_filetype': (ctypes.c_uint, [pointer]),
        'archive_read_data': (ctypes.c_ssize_t, [pointer, pointer, ctypes.c_size_t]),
        'archive_read_free': (ctypes.c_int, [pointer]),
        'archive_error_string': (ctypes.c_char_p, [pointer]),
    }
    for name, (result, args) in signatures.items():
        function = getattr(lib, name)
        function.restype, function.argtypes = result, args
    tools = BUILD / 'commercial61-tools-001/root'
    payload = BUILD / 'commercial61-iso-001/payload.squashfs'
    env = dict(os.environ, LD_LIBRARY_PATH=str(tools / 'usr/lib/x86_64-linux-gnu'))
    command = [str(tools / 'usr/bin/unsquashfs'), '-cat', str(payload), 'state-seed.tar.zst']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    reader = lib.archive_read_new()
    assert reader
    count, rows = 0, []
    try:
        for code in [lib.archive_read_support_filter_all(reader),
                     lib.archive_read_support_format_tar(reader),
                     lib.archive_read_open_fd(reader, process.stdout.fileno(), 65536)]:
            assert code == 0, lib.archive_error_string(reader)
        entry = pointer()
        buffer = ctypes.create_string_buffer(1024 * 1024)
        while True:
            code = lib.archive_read_next_header(reader, ctypes.byref(entry))
            if code == 1:
                break
            assert code == 0, lib.archive_error_string(reader)
            count += 1
            name = lib.archive_entry_pathname(entry).decode('utf-8', errors='strict')
            size = lib.archive_entry_size(entry)
            kind = lib.archive_entry_filetype(entry)
            if observe is not None:
                observe(name, size, kind)
            if consume is not None:
                consume(name, size, kind, lib, reader, entry)
            if not select(name) or kind != 0o100000:
                continue
            assert 0 < size <= 128 * 1024 * 1024, size
            chunks = []
            while True:
                length = lib.archive_read_data(reader, buffer, len(buffer))
                assert length >= 0, lib.archive_error_string(reader)
                if length == 0:
                    break
                chunks.append(buffer.raw[:length])
            data = b''.join(chunks)
            assert len(data) == size
            rows.append(dict(path=name, **inspect(data)))
        # Drain compressed trailing padding so the producer can exit normally.
        lib.archive_read_free(reader)
        reader = None
        while process.stdout.read(1024 * 1024):
            pass
        error = process.stderr.read()
        assert process.wait(timeout=30) == 0, error.decode(errors='replace')
    finally:
        if reader:
            lib.archive_read_free(reader)
        process.stdout.close()
        if process.poll() is None:
            process.kill()
        process.wait()
        process.stderr.close()
    return dict(entries_inspected=count, selected_files=rows,
                payload=str(payload), seed_member='state-seed.tar.zst',
                all_tar_entry_names_inspected=True, files_extracted=False,
                target_modified=False, signature_checks_changed=False)


def scan_seed():
    result = scan_archive()
    result['settings_haps'] = result.pop('selected_files')
    result['content_read_scope'] = 'Settings-related regular HAP entries only'
    return result


if __name__ == '__main__':
    folder = ROOT / 'reports/settings-seed-183'
    assert not folder.exists(), 'immutable result already exists'
    result = scan_seed()
    manifest = ROOT / 'reports/commercial61-iso-001/result.json'
    result['payload_sha256_from_existing_manifest'] = json.loads(manifest.read_text())['payload_sha256']
    result['payload_rehashed_this_scan'] = False
    folder.mkdir()
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
