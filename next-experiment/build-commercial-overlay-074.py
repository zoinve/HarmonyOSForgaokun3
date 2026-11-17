"""Bounded incremental overlay over exact installed 073; preserve shared 072."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import runpy

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
work = root / 'commercial61-native-074'
report = b.parent / 'reports/commercial61-native-074'
tree = ast.parse(runpy.run_path(str(b / 'build-native-return-overlay-033.py'))['payload'])
helpers = {}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))],
                      type_ignores=[]), 'archive-helpers', 'exec'), helpers)
parse, member = helpers['parse'], helpers['member']
before = parse(root / 'commercial61-native-073/initrd.img')
after = parse(work / 'initrd.img')
assert set(before) <= set(after)
patch = {name: item for name, item in after.items() if name not in before or before[name] != item}
assert set(patch) == {'init', 'native-target/bootstrap', 'native-target/allocator074',
    'native-target/allocator074/libdisplay_buffer_vdi_impl.z.so', 'native-target/egl074',
    'native-target/egl074/libEGL_impl.so'}
assert dict(before, **patch) == after
parent = root / 'commercial61-native-073/minimal-overlay.img'
parent_record = json.loads((b.parent / 'reports/commercial61-native-073/overlay-result.json').read_text())
assert hashlib.sha256(parent.read_bytes()).hexdigest() == parent_record['sha256']
data = b''.join(member(name, mode, body, i + 1) for i, (name, (mode, body)) in enumerate(sorted(patch.items())))
data += member('TRAILER!!!', 0, b'', len(patch) + 1)
blob = gzip.compress(data, compresslevel=9, mtime=0)
assert len(blob) < 2 * 1024 * 1024
(work / 'minimal-overlay.img').open('xb').write(blob)
assert parse(work / 'minimal-overlay.img') == patch
result = dict(bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(), members=sorted(patch),
    chain=parent_record['chain'] + ['commercial61-native-074/initrd.img'],
    shared_parent_overlay_sha256=parent_record['sha256'],
    existing_016_overlay_sha256=parent_record['existing_016_overlay_sha256'],
    software_backend_parent_sha256=parent_record['shared_parent_overlay_sha256'],
    parent_directories_present_before_hardware_files=True, ordered_chain_equals_full_074=True,
    original_images_written=False, sdk_payload=False, runtime_verified=False)
for folder in [work, report]:
    (folder / 'overlay-result.json').open('x').write(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
