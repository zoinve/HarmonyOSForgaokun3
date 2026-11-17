"""Replace shipped modules and indexes with the isolated kernel490 build."""
from pathlib import Path
import gzip
import hashlib
import inspect
import json
import runpy
import shutil
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/compat-modules-500'
BUILD = Path('/home/zoinve/harmony-virgl-883')
RELEASE = '7.1.0-rc3-gaokun3-el2'


def capture():
    assert not REPORT.exists()
    workflow = runpy.run_path(str(ROOT / 'next-experiment/settings-workflow-254.py'))
    code = workflow['GUARD'] + r'''
entry=Path('/boot/efi/loader/entries/commercial61-native-471.conf')
assert entry.is_file()
refs=[line.split(None,1)[1] for line in entry.read_text().splitlines() if line.startswith('initrd ')]
assert len(refs)==len(set(refs)) and '/set471.img' in refs
assert all((Path('/boot/efi')/name.lstrip('/')).is_file() for name in refs)
print(json.dumps(dict(entry=entry.name,initrds=refs,ubuntu_default_preserved=True)))
'''
    result = workflow['remote'](code)
    REPORT.mkdir()
    (REPORT / 'references.json').open('x').write(result)
    print(result)


def build():
    work = BUILD / 'compat-modules-500'
    if work.exists():
        assert not any(work.iterdir()), 'only resume before any package writes'
    else:
        work.mkdir()
    reference = json.loads((REPORT / 'references.json').read_text())
    kernel = BUILD / 'compat-kernel-490/out'
    assert (kernel / 'include/config/kernel.release').read_text().strip() == RELEASE
    assert json.loads((ROOT / 'reports/compat-kernel-490/result.json').read_text())['matching_modules_built']
    member = runpy.run_path(str(ROOT / 'next-experiment/build-commercial-native-087.py'))['member']
    inventory = json.loads((REPORT / 'module-inventory.json').read_text())
    assert inventory['initrds'] == reference['initrds']
    paths = set(inventory['paths'])
    assert len(paths) > 100
    stage = work / 'root'
    modules = stage / 'lib/modules' / RELEASE
    modules.mkdir(parents=True)
    builtin = set((kernel / 'modules.builtin').read_text().splitlines())
    rows, removed = [], []
    for name in sorted(paths):
        relative = name.split('/kernel/', 1)[1]
        source = kernel / relative
        if 'kernel/' + relative in builtin:
            removed.append(name)
            continue
        assert source.is_file(), ('matching module missing', relative)
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        rows.append(dict(path=name, bytes=target.stat().st_size))
    for name in ['modules.builtin', 'modules.builtin.modinfo', 'modules.order']:
        shutil.copyfile(kernel / name, modules / name)
    with (REPORT / 'depmod.log').open('xb') as log:
        subprocess.run(['depmod', '-b', str(stage), '-F', str(kernel / 'System.map'), RELEASE],
                       stdout=log, stderr=subprocess.STDOUT, check=True, timeout=60)
    entries = {}
    for path in sorted(stage.rglob('*')):
        name = str(path.relative_to(stage))
        entries[name] = (0o40755, b'') if path.is_dir() else (0o100644, path.read_bytes())
    raw = b''.join(member(name, mode, data, index + 1)
                   for index, (name, (mode, data)) in enumerate(entries.items()))
    data = gzip.compress(raw + member('TRAILER!!!', 0, b'', len(entries) + 1), compresslevel=6, mtime=0)
    archive = work / 'modules.cpio.gz'
    archive.open('xb').write(data)
    result = dict(kernel='490', release=RELEASE, modules=len(rows),
        old_paths_now_builtin=removed, matching_modules=rows, archive=str(archive),
        bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
        installed=False, runtime_verified=False, ubuntu_modules_modified=False)
    (REPORT / 'result.json').open('x').write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'matching_modules'}, indent=2))


def inventory():
    output = REPORT / 'module-inventory.json'
    assert not output.exists()
    reference = json.loads((REPORT / 'references.json').read_text())
    workflow = runpy.run_path(str(ROOT / 'next-experiment/settings-workflow-254.py'))
    parser = runpy.run_path(str(ROOT / 'next-experiment/audit-commercial-network-inputs-079.py'))['members']
    code = workflow['GUARD'] + '\nimport gzip,lzma,stat\n' + inspect.getsource(parser)
    code += '\nrefs=' + repr(reference['initrds']) + '\nrelease=' + repr(RELEASE) + '\n'
    code += r'''
entry=Path('/boot/efi/loader/entries/commercial61-native-471.conf')
assert [line.split(None,1)[1] for line in entry.read_text().splitlines() if line.startswith('initrd ')]==refs
paths=set()
for ref in refs:
 archive=(Path('/boot/efi')/ref.lstrip('/')).read_bytes()
 unpacked=lzma.decompress(archive) if archive.startswith(b'\xfd7zXZ\x00') else gzip.decompress(archive)
 for name,mode,data in members(unpacked):
  if name.startswith('lib/modules/'+release+'/kernel/') and name.endswith('.ko'):
   assert stat.S_ISREG(mode)
   paths.add(name)
print(json.dumps(dict(initrds=refs,paths=sorted(paths),files_written=False,hash_suite_run=False)))
'''
    result = workflow['remote'](code, timeout=120)
    output.open('x').write(result)
    print('Exact shipped module paths:', len(json.loads(result)['paths']))


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['capture', 'inventory', 'build']
    dict(capture=capture, inventory=inventory, build=build)[sys.argv[1]]()
