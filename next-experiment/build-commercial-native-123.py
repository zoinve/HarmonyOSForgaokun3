"""Load a hash-verified minimal SettingsData seed; preserve original services."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def adapt(source, seed):
    path = '/mnt/ubuntu' + seed['seed_path']
    expected = seed['seed_sha256']
    destination = '/native-target/scratch-data.ext4'
    command = (f'test -f {path} && test ! -L {path} && '
        f'test "$(/bin/busybox sha256sum {path})" = "{expected}  {path}" && '
        f'test -f {destination} && test ! -L {destination} && '
        f'/bin/busybox cp {path} {destination} && '
        f'test "$(/bin/busybox sha256sum {destination})" = "{expected}  {destination}" && '
        'echo OOBE123_SEED_VERIFIED original_images_unchanged=1 local_setup_flags=1 commercial_activation_unchanged=1')
    addition = ('    if(okay){\n        char *seed123[]={"/bin/busybox","sh","-c",' +
        json.dumps(command) + ',NULL};\n        if(probe("oobe-seed-load123",seed123,12))okay=0;\n    }\n\n')
    anchor = '    if(okay){\n\n        char memory010[8192];'
    assert source.count(anchor) == 1
    return source.replace(anchor, addition + anchor, 1)


if __name__ == '__main__':
    work, report = BUILD / 'commercial61-native-123', ROOT / 'reports/commercial61-native-123'
    assert not work.exists() and not report.exists()
    seed = json.loads((ROOT / 'reports/oobe-seed-preparation-123/result.json').read_text())
    assert seed['seed_e2fsck_status'] == 0 and seed['seed_bytes'] == 536870912
    assert seed['only_local_first_run_settings_modified'] and not seed['sceneboard_cache_copied']
    assert all(d['schema_preserved'] and d['unrelated_rows_preserved'] and d['all_xattrs_preserved'] for d in seed['databases'])
    parent = BUILD / 'commercial61-native-121'
    baseline = BUILD / 'commercial61-native-116'
    metadata = json.loads((ROOT / 'reports/commercial61-native-121/result.json').read_text())
    for item in metadata['artifacts']:
        assert sha((parent / item['name']).read_bytes()) == item['sha256']
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    before = {n: (mode, data) for n, mode, data in parse(gzip.decompress((parent / 'initrd.img').read_bytes()))}
    after = dict(before)
    # Drop the one-time snapshot instrumentation by returning to the exact 116 outer baseline.
    outer = adapt((baseline / 'init.c').read_text(), seed)
    assert 'oobe_snapshot121' not in outer and 'oobe-data-snapshot-121.h' not in outer
    work.mkdir()
    report.mkdir()
    for item in metadata['artifacts']:
        if item['name'] not in ('init', 'init.c', 'initrd.img'):
            (work / item['name']).open('xb').write((parent / item['name']).read_bytes())
    (work / 'init.c').open('x').write(outer)
    compiled = subprocess.run(['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
        str(work / 'init.c'), '-I', str(BASE), str(BASE / 'baremetal-diagnostic-core.c'), '-o', str(work / 'init')], capture_output=True)
    (report / 'init.stdout').open('xb').write(compiled.stdout)
    (report / 'init.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr.decode(errors='replace')
    after['init'] = (before['init'][0], (work / 'init').read_bytes())
    wrapper = before['early-hardware093.sh'][1]
    assert wrapper.count(sha(before['init'][1]).encode()) == 1
    after['early-hardware093.sh'] = (before['early-hardware093.sh'][0],
        wrapper.replace(sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1))
    delta = {n: value for n, value in after.items() if value != before.get(n)}
    assert set(delta) == {'init', 'early-hardware093.sh'}
    def archive(entries):
        raw = b''.join(pack(n, mode, data, i + 1) for i, (n, (mode, data)) in enumerate(entries.items()))
        return gzip.compress(raw + pack('TRAILER!!!', 0, b'', len(entries) + 1), compresslevel=6, mtime=0)
    (work / 'initrd.img').open('xb').write(archive(after))
    overlay = archive(delta)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    previous = json.loads((ROOT / 'reports/commercial61-native-121/overlay-result.json').read_text())
    overlay_result = dict(bytes=len(overlay), sha256=sha(overlay), members=sorted(delta),
        chain=previous['chain'] + ['commercial61-native-123/initrd.img'],
        shared_parent_overlay_sha256=previous['sha256'], ordered_chain_equals_full_123=True,
        existing_016_overlay_sha256=previous['existing_016_overlay_sha256'],
        original_images_written=False, runtime_verified=False)
    metadata['artifacts'] = [dict(name=i['name'], bytes=(work / i['name']).stat().st_size,
        sha256=sha((work / i['name']).read_bytes())) for i in metadata['artifacts']]
    metadata['oobe123'] = dict(parent='commercial61-native-121', executable_baseline='commercial61-native-116',
        seed_path=seed['seed_path'], seed_sha256=seed['seed_sha256'], seed_bytes=seed['seed_bytes'],
        original_runtime_unchanged=True, settings_modified=True, setup_flags_user_authorized=True,
        sceneboard_cache_copied=False, commercial_activation_modified=False,
        snapshot_instrumentation_removed=True, installed=False, target_boot_performed=False)
    metadata['runtime_verified'] = False
    for directory in (work, report):
        (directory / 'result.json').open('x').write(json.dumps(metadata, indent=2))
        (directory / 'overlay-result.json').open('x').write(json.dumps(overlay_result, indent=2))
    (report / 'seed-provenance.json').open('x').write(json.dumps(seed, indent=2))
    print(json.dumps(metadata['oobe123'], indent=2))
