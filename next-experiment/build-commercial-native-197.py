'''Isolate Settings state while keeping desktop173 runtime byte-identical.'''
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess
import uuid

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')
RUNTIME = 'fe80eef0831fda293ff0bbebb66f9c2d0c6c8c6b739b47cc8714653479ea7122'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parent = BUILD / 'commercial61-native-173'
    work = BUILD / 'commercial61-native-197-r1'
    report = ROOT / 'reports/commercial61-native-197-r1'
    assert not work.exists() and not report.exists(), 'preserve numbered evidence'
    candidate = json.loads((ROOT / 'reports/settings-data-candidate-191-r2/result.json').read_text())
    assert candidate['candidate_unmounted'] and candidate['offline_fsck_status'] == 0
    assert candidate['original_bms_token_databases_unmodified']
    metadata = json.loads((parent / 'result.json').read_text())
    previous = json.loads((parent / 'overlay-result.json').read_text())
    for row in metadata['artifacts']:
        assert sha((parent / row['name']).read_bytes()) == row['sha256']
    assert sha((parent / 'bootstrap-runtime087').read_bytes()) == RUNTIME
    assert sha((parent / 'minimal-overlay.img').read_bytes()) == previous['sha256']
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    member = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    before = {n: (m, b) for n, m, b in parser(gzip.decompress((parent / 'initrd.img').read_bytes()))}
    work.mkdir()
    report.mkdir()
    for row in metadata['artifacts']:
        if row['name'] not in {'init', 'init.c', 'initrd.img'}:
            (work / row['name']).open('xb').write((parent / row['name']).read_bytes())
    header = (BASE / 'persistent-data-166.h').read_bytes()
    assert header.count(b'harmony-persistent-data-165') == 2
    header = header.replace(b'harmony-persistent-data-165', b'harmony-settings-data-197')
    (work / 'persistent-data-166.h').open('xb').write(header)
    for name, directory in [('persistent-data-172.h', BASE), ('native-live-debug-159.h', parent)]:
        (work / name).open('xb').write((directory / name).read_bytes())
    source = (parent / 'init.c').read_text()
    old = '/commercial61-native-173/bootstrap-runtime087'
    assert source.count(old) == 5
    source = source.replace(old, '/commercial61-native-197/bootstrap-runtime087')
    lines = source.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.startswith('#define PERSISTENT166_UUID ')]
    assert len(matches) == 1
    values = ','.join(str(value) for value in uuid.UUID(candidate['candidate_uuid']).bytes)
    lines[matches[0]] = '#define PERSISTENT166_UUID {' + values + '}\n'
    (work / 'init.c').open('x').write(''.join(lines))
    command = ['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
               '-I', str(BASE), str(work / 'init.c'), str(BASE / 'baremetal-diagnostic-core.c'),
               '-o', str(work / 'init')]
    compiled = subprocess.run(command, capture_output=True, timeout=120)
    (report / 'init.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr.decode()
    after = dict(before)
    after['init'] = (before['init'][0], (work / 'init').read_bytes())
    mode, wrapper = before['early-hardware093.sh']
    assert wrapper.count(sha(before['init'][1]).encode()) == 1
    after['early-hardware093.sh'] = (mode, wrapper.replace(
        sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1))
    delta = {n: value for n, value in after.items() if before.get(n) != value}
    assert set(delta) == {'init', 'early-hardware093.sh'}

    def archive(entries):
        raw = b''.join(member(n, m, b, i + 1) for i, (n, (m, b)) in enumerate(entries.items()))
        return gzip.compress(raw + member('TRAILER!!!', 0, b'', len(entries) + 1), compresslevel=6, mtime=0)

    (work / 'initrd.img').open('xb').write(archive(after))
    minimal = {n: (m, b) for n, m, b in parser(gzip.decompress((parent / 'minimal-overlay.img').read_bytes()))}
    minimal.update(delta)
    overlay = archive(minimal)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    chain = previous['chain'][:-1] + ['commercial61-native-197/initrd.img']
    assert previous['ordered_chain_equals_full_173']
    merged = dict(before)
    merged.update({n: (m, b) for n, m, b in parser(gzip.decompress(overlay))})
    assert merged == after, 'pinned full parent plus new overlay must equal full image'
    for name in ('bootstrap-runtime087', 'bootstrap-runtime087.c'):
        assert (work / name).read_bytes() == (parent / name).read_bytes()
    metadata['artifacts'] = [dict(name=row['name'], bytes=(work / row['name']).stat().st_size,
        sha256=sha((work / row['name']).read_bytes())) for row in metadata['artifacts']]
    metadata['runtime_verified'] = False
    metadata['persistent166'].update(data_path='/mnt/lab/harmony-settings-data-197/data.ext4',
        filesystem_uuid=candidate['candidate_uuid'], persistent_header_sha256=sha(header),
        cross_boot_persistence_verified=False)
    metadata['settings197'] = dict(source_candidate_sha256=candidate['candidate_sha256'],
        runtime173_byte_identical=True, runtime_source173_byte_identical=True,
        active_data165_modified=False, original_signature_checks_changed=False,
        installed_or_booted=False, settings_ui_verified=False, usb_work_paused=True)
    result = dict(previous, bytes=len(overlay), sha256=sha(overlay), chain=chain,
        changed_from_full_parent=sorted(delta), ordered_chain_equals_full_197=True)
    result['chain_verification_basis'] = 'inherited173_chain_and_replayed_pinned_full173_plus197_overlay'
    result['full_historical_chain_independently_replayed'] = False
    result['parent_full_sha256'] = sha((parent / 'initrd.img').read_bytes())
    result.pop('ordered_chain_equals_full_173')
    for folder in (work, report):
        (folder / 'result.json').open('x').write(json.dumps(metadata, indent=2))
        (folder / 'overlay-result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(metadata['settings197'], indent=2))


if __name__ == '__main__':
    main()
