"""Add passive original-memory-service diagnostics to the admitted 108 chain."""
from pathlib import Path
import gzip
import hashlib
import json
import lzma
import runpy
import shutil
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def monitor_source(original):
    anchor = "printf 'MEMMGR108_OBSERVER_BEGIN original_service_only=1 no_start_stop_commands=1\\n'\n"
    assert original.count(anchor) == 1
    return original.replace(anchor, '/system/bin/sh /commercial-memmgr-stack109.sh &\n' + anchor, 1)


def outer_source(original):
    anchor = '"commercial-memmgr108.log"'
    assert original.count(anchor) == 1
    return original.replace(anchor, anchor + ',"commercial-memmgr-stack109.log"', 1)


if __name__ == '__main__':
    work, report = BUILD / 'commercial61-native-109', ROOT / 'reports/commercial61-native-109'
    assert not work.exists() and not report.exists()
    parent = BUILD / 'commercial61-native-108'
    previous = json.loads((ROOT / 'reports/commercial61-native-108/result.json').read_text())
    for item in previous['artifacts']:
        assert sha((parent / item['name']).read_bytes()) == item['sha256']
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    def members(path):
        body = path.read_bytes()
        raw = lzma.decompress(body) if body.startswith(b'\xfd7zXZ') else gzip.decompress(body)
        return {n: (m, d) for n, m, d in parse(raw)}
    before = members(parent / 'initrd.img')
    after = dict(before)
    work.mkdir()
    report.mkdir()
    for item in previous['artifacts']:
        if item['name'] not in {'init', 'init.c', 'initrd.img'}:
            shutil.copyfile(parent / item['name'], work / item['name'])
    source = outer_source((parent / 'init.c').read_text())
    (work / 'init.c').open('x').write(source)
    (report / 'init.c').open('x').write(source)
    command = ['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
        str(work / 'init.c'), '-I', str(BASE), str(BASE / 'baremetal-diagnostic-core.c'), '-o', str(work / 'init')]
    compiled = subprocess.run(command, capture_output=True)
    (report / 'init.stdout').open('xb').write(compiled.stdout)
    (report / 'init.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr.decode(errors='replace')
    after['init'] = (before['init'][0], (work / 'init').read_bytes())
    wrapper = before['early-hardware093.sh'][1]
    assert wrapper.count(sha(before['init'][1]).encode()) == 1
    after['early-hardware093.sh'] = (before['early-hardware093.sh'][0], wrapper.replace(
        sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1))
    monitor = monitor_source(before['native-target/commercial-memmgr108.sh'][1].decode()).encode()
    after['native-target/commercial-memmgr108.sh'] = (0o100755, monitor)
    observer = (BASE / 'commercial-memmgr-stack-109.sh').read_bytes()
    name = 'native-target/commercial-memmgr-stack109.sh'
    assert name not in before
    after[name] = (0o100755, observer)
    def archive(entries):
        raw = b''.join(pack(n, m, d, i + 1) for i, (n, (m, d)) in enumerate(entries.items()))
        raw += pack('TRAILER!!!', 0, b'', len(entries) + 1)
        return gzip.compress(raw, compresslevel=6, mtime=0)
    (work / 'initrd.img').open('xb').write(archive(after))
    parent_overlay = json.loads((ROOT / 'reports/commercial61-native-108/overlay-result.json').read_text())
    merged = {}
    for relative in parent_overlay['chain']:
        number, filename = relative.split('/')
        if filename == 'early094.img':
            path = BUILD / 'commercial61-native-094/minimal-overlay.img'
        elif number == 'commercial61-native-001':
            path = BUILD / number / filename
        elif number == 'commercial61-native-016':
            path = BUILD / 'commercial61-native-016-r2/minimal-overlay.img'
        elif number == 'commercial61-native-072':
            path = BUILD / number / 'minimal-overlay-xz.img'
        else:
            path = BUILD / number / 'minimal-overlay.img'
        merged.update(members(path))
    assert merged == before
    delta = {n: v for n, v in after.items() if before.get(n) != v}
    assert set(delta) == {'init', 'early-hardware093.sh', 'native-target/commercial-memmgr108.sh', name}
    overlay_body = archive(delta)
    (work / 'minimal-overlay.img').open('xb').write(overlay_body)
    merged.update(members(work / 'minimal-overlay.img'))
    assert merged == after
    overlay = dict(bytes=len(overlay_body), sha256=sha(overlay_body), members=sorted(delta),
        chain=parent_overlay['chain'] + ['commercial61-native-109/initrd.img'],
        shared_parent_overlay_sha256=parent_overlay['sha256'], ordered_chain_equals_full_109=True,
        existing_016_overlay_sha256=parent_overlay['existing_016_overlay_sha256'],
        original_images_written=False, runtime_verified=False)
    previous['artifacts'] = [dict(name=item['name'], bytes=(work / item['name']).stat().st_size,
        sha256=sha((work / item['name']).read_bytes())) for item in previous['artifacts']]
    previous['memstack109'] = dict(parent='commercial61-native-108',
        observer_sha256=sha(observer), monitor_sha256=sha(monitor),
        runtime_path=previous['memmgr108']['runtime_path'],
        runtime_sha256=sha((work / 'bootstrap-runtime087').read_bytes()),
        runtime_byte_identical_to_108=True, changed_archive_members=sorted(delta),
        original_services_wrappers_tokens_identity_and_recovery_unchanged=True,
        observation_can_perturb_timing=True, runtime_verified=False)
    previous['runtime_verified'] = False
    for directory in (work, report):
        (directory / 'result.json').open('x').write(json.dumps(previous, indent=2))
        (directory / 'overlay-result.json').open('x').write(json.dumps(overlay, indent=2))
    (report / 'observer109.sh').open('xb').write(observer)
    (report / 'monitor108.sh').open('xb').write(monitor)
    print(json.dumps(dict(metadata=previous['memstack109'], overlay=overlay), indent=2))
