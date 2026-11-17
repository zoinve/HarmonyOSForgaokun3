"""Verify the complete ordered initrd chain including matching modules."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import runpy
import stat

BASE = Path(__file__).resolve().parent
ROOT = Path('/home/zoinve/harmony-virgl-883')


def main():
    tree = ast.parse(runpy.run_path(str(BASE / 'build-native-return-overlay-033.py'))['payload'])
    helpers = {}
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))], type_ignores=[]), 'archive-helpers', 'exec'), helpers)
    parse, member = helpers['parse'], helpers['member']
    work = ROOT / 'commercial61-native-047'
    local = BASE.parent / 'reports/commercial61-native-047'
    dest = work / 'minimal-overlay.img'
    assert not dest.exists() and not (local / 'overlay-result.json').exists()
    state = parse(ROOT / 'commercial61-native-001/initrd.img')
    state.update(parse(ROOT / 'commercial61-native-017/minimal-overlay.img'))
    state.update(parse(ROOT / 'commercial61-native-016-r2/minimal-overlay.img'))
    new = parse(work / 'initrd.img')
    old = parse(ROOT / 'commercial61-native-046/initrd.img')
    for name, value in old.items():
        if name == 'init' or name == 'hmos_ashmem.ko' or name.startswith('lib/modules/'):
            continue
        assert new[name] == value, ('unrelated change', name)
    assert not set(old) - set(new)
    patch = {name: value for name, value in new.items() if state.get(name) != value}
    ordered = sorted(patch, key=lambda name: (len(Path(name).parts), name))
    for name in ordered:
        for parent in Path(name).parents:
            if str(parent) == '.':
                continue
            assert str(parent) in state and stat.S_ISDIR(state[str(parent)][0]), name
        state[name] = patch[name]
    assert state == new
    data = b''.join(member(name, patch[name][0], patch[name][1], i + 1) for i, name in enumerate(ordered))
    data += member('TRAILER!!!', 0, b'', len(ordered) + 1)
    dest.open('xb').write(gzip.compress(data, compresslevel=9, mtime=0))
    result = dict(sha256=hashlib.sha256(dest.read_bytes()).hexdigest(), bytes=dest.stat().st_size,
                  changed_members=ordered, ordered_chain_equals_full_047=True,
                  original_userland_unchanged=True, matching_modules_included=True)
    for path in [work / 'overlay-result.json', local / 'overlay-result.json']:
        path.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'changed_members'}, indent=2))


if __name__ == '__main__':
    main()
