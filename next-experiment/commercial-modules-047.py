"""Replace all initrd modules with matching builds and regenerate subset indexes."""
from pathlib import Path
import hashlib
import json
import runpy
import shutil
import stat
import subprocess

BASE = Path(__file__).resolve().parents[1]


def replace_modules(entries, work, local):
    build = json.loads((BASE / 'reports/native-trace-kernel-047/result.json').read_text())
    ashmem = json.loads((BASE / 'reports/native-ashmem-module-047/result.json').read_text())
    assert build['previous_unchanged'] and build['configuration_unchanged']
    source = Path(build['modules_root'])
    release = source.name
    prefix = 'lib/modules/' + release + '/'
    selected = {name.removeprefix(prefix) for name in entries
                if name.startswith(prefix) and name.endswith('.ko')}
    assert len(selected) > 300
    deps = {}
    for line in (source / 'modules.dep').read_text().splitlines():
        name, required = line.split(':', 1)
        deps[name] = required.split()
    pending = list(selected)
    while pending:
        name = pending.pop()
        assert name in deps, name
        for dep in deps[name]:
            if dep not in selected:
                selected.add(dep)
                pending.append(dep)
    stage = work / 'module-stage'
    target = stage / prefix
    target.mkdir(parents=True)
    for name in sorted(selected):
        original = source / name
        digest = hashlib.sha256(original.read_bytes()).hexdigest()
        assert digest == build['modules'][name]
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, destination)
    for name in ['modules.builtin', 'modules.builtin.modinfo', 'modules.order']:
        if (source / name).is_file():
            shutil.copyfile(source / name, target / name)
    result = subprocess.run(['depmod', '-b', str(stage), release], capture_output=True)
    (local / 'depmod.stdout').open('xb').write(result.stdout)
    (local / 'depmod.stderr').open('xb').write(result.stderr)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    before = dict(entries)
    for path in sorted(stage.rglob('*'), key=lambda p: (len(p.parts), str(p))):
        name = str(path.relative_to(stage))
        if path.is_dir():
            entries.setdefault(name, (stat.S_IFDIR | 0o755, b''))
        else:
            entries[name] = (stat.S_IFREG | 0o644, path.read_bytes())
    module = Path(ashmem['module'])
    assert hashlib.sha256(module.read_bytes()).hexdigest() == ashmem['sha256']
    entries['hmos_ashmem.ko'] = (before['hmos_ashmem.ko'][0], module.read_bytes())
    expected = {'hmos_ashmem.ko'} | {name for name in entries if name.startswith(prefix)}
    changed = {name for name in entries if entries[name] != before.get(name)}
    assert all(name in expected or stat.S_ISDIR(entries[name][0]) for name in changed)
    assert all(not name.endswith('.ko') or name in expected for name in entries)
    sizes = runpy.run_path(str(BASE / 'next-experiment/audit-native-trace-modules-047.py'))['module_size']
    assert {sizes(target / name)['bytes'] for name in selected} == {1216}
    assert sizes(module)['bytes'] == 1216
    manifest = dict(release=release, selected_modules=len(selected),
                    ashmem_rebuilt=True, all_module_structure_bytes=1216,
                    changed_members=sorted(changed), dependency_closure_verified=True,
                    indexes_regenerated=True, source_build=build['image_sha256'],
                    module_sha256={name: hashlib.sha256(entries[name][1]).hexdigest()
                                   for name in entries if name.endswith('.ko')})
    (local / 'module-provenance.json').open('x').write(json.dumps(manifest, indent=2))
