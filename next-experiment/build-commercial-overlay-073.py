"""Tiny incremental archive over the installed hash-pinned 072 XZ overlay."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import lzma
import runpy

base = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
work = root / 'commercial61-native-073'
report = base.parent / 'reports/commercial61-native-073'
tree = ast.parse(runpy.run_path(str(base / 'build-native-return-overlay-033.py'))['payload'])
helpers = {}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))], type_ignores=[]), 'archive-helpers', 'exec'), helpers)
parse, member = helpers['parse'], helpers['member']
before = parse(root / 'commercial61-native-072/initrd.img')
after = parse(work / 'initrd.img')
assert set(before) <= set(after)
patch = {name: item for name, item in after.items() if name not in before or before[name] != item}
assert set(patch) == {'init', 'native-target/bootstrap', 'native-target/allocator073',
    'native-target/allocator073/libdisplay_buffer_vdi_impl.z.so'}
state = dict(before)
state.update(patch)
assert state == after
parent = root / 'commercial61-native-072/minimal-overlay-xz.img'
parent_record = json.loads((base.parent / 'reports/commercial61-native-072/overlay-result-xz.json').read_text())
assert hashlib.sha256(parent.read_bytes()).hexdigest() == parent_record['sha256']
assert lzma.decompress(parent.read_bytes()) == gzip.decompress((root / 'commercial61-native-072/minimal-overlay.img').read_bytes())
data = b''.join(member(name, mode, body, i + 1) for i, (name, (mode, body)) in enumerate(sorted(patch.items())))
data += member('TRAILER!!!', 0, b'', len(patch) + 1)
blob = gzip.compress(data, compresslevel=9, mtime=0)
assert len(blob) < 2 * 1024 * 1024
with (work / 'minimal-overlay.img').open('xb') as f:
    f.write(blob)
assert parse(work / 'minimal-overlay.img') == patch
result = dict(bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(), members=sorted(patch),
    chain=['commercial61-native-001/initrd.img', 'commercial61-native-017/initrd.img',
        'commercial61-native-016/initrd.img', 'commercial61-native-072/initrd.img',
        'commercial61-native-073/initrd.img'], shared_parent_overlay_sha256=parent_record['sha256'],
    existing_016_overlay_sha256=parent_record['existing_016_overlay_sha256'],
    parent_directories_present_before_hardware_files=True, ordered_chain_equals_full_073=True,
    original_images_written=False, sdk_payload=False, runtime_verified=False)
for directory in [work, report]:
    with (directory / 'overlay-result.json').open('x') as f:
        json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
