"""Verify the full ordered chain while packing only 108's added scaffolding."""
from pathlib import Path
import gzip
import hashlib
import json
import lzma
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


if __name__ == '__main__':
    work, report = BUILD / 'commercial61-native-108', ROOT / 'reports/commercial61-native-108'
    assert not (work / 'minimal-overlay.img').exists() and not (report / 'overlay-result.json').exists()
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    def members(path):
        body = path.read_bytes()
        raw = lzma.decompress(body) if body.startswith(b'\xfd7zXZ') else gzip.decompress(body)
        return {n: (m, d) for n, m, d in parse(raw)}
    before = members(BUILD / 'commercial61-native-107/initrd.img')
    after = members(work / 'initrd.img')
    assert set(before) <= set(after)
    patch = {n: v for n, v in after.items() if before.get(n) != v}
    assert set(patch) == {'init', 'early-hardware093.sh', 'native-target/commercial-memmgr108.sh'}
    parent = json.loads((ROOT / 'reports/commercial61-native-107/overlay-result.json').read_text())
    merged = {}
    for relative in parent['chain']:
        number, name = relative.split('/')
        if name == 'early094.img':
            path = BUILD / 'commercial61-native-094/minimal-overlay.img'
        elif number == 'commercial61-native-001':
            path = BUILD / number / name
        elif number == 'commercial61-native-016':
            path = BUILD / 'commercial61-native-016-r2/minimal-overlay.img'
        elif number == 'commercial61-native-072':
            path = BUILD / number / 'minimal-overlay-xz.img'
        else:
            path = BUILD / number / 'minimal-overlay.img'
        merged.update(members(path))
    assert merged == before
    raw = b''.join(pack(n, m, d, i + 1) for i, (n, (m, d)) in enumerate(patch.items()))
    raw += pack('TRAILER!!!', 0, b'', len(patch) + 1)
    body = gzip.compress(raw, compresslevel=6, mtime=0)
    merged.update({n: (m, d) for n, m, d in parse(gzip.decompress(body))})
    assert merged == after
    (work / 'minimal-overlay.img').open('xb').write(body)
    result = dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), members=sorted(patch),
        chain=parent['chain'] + ['commercial61-native-108/initrd.img'],
        shared_parent_overlay_sha256=parent['sha256'], ordered_chain_equals_full_108=True,
        existing_016_overlay_sha256=parent['existing_016_overlay_sha256'],
        original_images_written=False, runtime_verified=False)
    for directory in (work, report):
        (directory / 'overlay-result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
