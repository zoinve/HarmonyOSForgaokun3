"""Verify the entire inherited initrd chain equals the new full RAM archive."""
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
    report = ROOT/'reports/commercial61-native-095'
    work = BUILD/'commercial61-native-095'
    dest = work/'minimal-overlay.img'
    assert not dest.exists() and not (report/'overlay-result.json').exists()
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE/'build-commercial-native-087.py'))['member']
    def members(path):
        body = path.read_bytes()
        raw = lzma.decompress(body) if body.startswith(b'\xfd7zXZ') else gzip.decompress(body)
        return {n: (m, d) for n, m, d in parse(raw)}
    before = members(BUILD/'commercial61-native-094/initrd.img')
    after = members(work/'initrd.img')
    assert set(before) <= set(after)
    patch = {n: v for n, v in after.items() if before.get(n) != v}
    assert set(patch) == {'native-target/commercial-desktop077.sh', 'native-target/native-normal-close095',
                          'native-target/commercial-focus095.awk', 'native-target/commercial-normal-close095.sh'}
    parent = json.loads((ROOT/'reports/commercial61-native-094/overlay-result.json').read_text())
    raw = b''.join(pack(n, m, d, i+1) for i, (n, (m, d)) in enumerate(patch.items()))
    raw += pack('TRAILER!!!', 0, b'', len(patch)+1)
    body = gzip.compress(raw, compresslevel=6, mtime=0)
    # Earlier chains include overlays stored in a different numbered directory.
    merged = {}
    for relative in parent['chain']:
        number, name = relative.split('/')
        if name == 'early094.img':
            path = BUILD/'commercial61-native-094/minimal-overlay.img'
        elif number == 'commercial61-native-001':
            path = BUILD/number/name
        elif number == 'commercial61-native-016':
            path = BUILD/'commercial61-native-016-r2/minimal-overlay.img'
        elif number == 'commercial61-native-072':
            path = BUILD/number/'minimal-overlay-xz.img'
        else:
            path = BUILD/number/'minimal-overlay.img'
        merged.update(members(path))
    assert merged == before, 'Inherited chain differs from full 094 archive'
    # Validate the packed delta in memory before writing its immutable artifact.
    merged.update({n: (m, d) for n, m, d in parse(gzip.decompress(body))})
    assert merged == after
    dest.open('xb').write(body)
    result = dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), members=sorted(patch),
        chain=parent['chain']+['commercial61-native-095/initrd.img'],
        shared_parent_overlay_sha256=parent['sha256'], ordered_chain_equals_full_095=True,
        existing_016_overlay_sha256=parent['existing_016_overlay_sha256'],
        original_images_written=False, sdk_payload=False, runtime_verified=False)
    for folder in (work, report):
        (folder/'overlay-result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
