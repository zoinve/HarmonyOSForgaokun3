"""Coherent software Mesa replacement; preserve the traced bridge and runtimes."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib, json, re, shutil, subprocess
root = Path('/home/zoinve/harmony-virgl-883')
reports = Path('/mnt/d/lab/HarmonyOSForMatebookego/reports')
report = reports/'original-graphics-egl-008'
work = root/'original-graphics-egl-008'
assert not report.exists() and not work.exists()
old = json.loads((reports/'original-graphics-egl-007/result.json').read_text())
software = json.loads((reports/'original-softpipe-001/result.json').read_text())
assert software['gallium_drivers'] == ['softpipe'] and software['original_build_unchanged']
assert old['platform_abi']=='std::__h' and not old['platform_libcxx_replaced']
replacements = {row['name']:row for row in software['files']}
assert len(replacements) == 6
retained = {'libEGL_impl.so', 'harmony-mesa/libc++_shared.so', 'harmony-mesa/libdrm.so.2'}
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
work.mkdir(exist_ok=False)
report.mkdir(exist_ok=False)
files = []
replaced = 0
for row in old['files']:
    name = row['name']
    if name in retained:
        selected = row
    else:
        assert name.startswith('harmony-mesa/')
        selected = replacements[name[len('harmony-mesa/'):]]
        replaced += 1
    source = Path(selected['path'])
    assert digest(source) == selected['sha256'] and source.stat().st_size == selected['bytes']
    dest = work/'bundle'/name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
    assert digest(dest) == selected['sha256']
    dynamic = subprocess.check_output(['llvm-readelf-19', '-dW', str(dest)], text=True)
    needed = re.findall(r'\(NEEDED\).*?\[(.*?)\]', dynamic)
    (report/(name.replace('/', '_')+'.dynamic.txt')).write_text(dynamic)
    files.append(dict(name=name, path=str(dest), sha256=digest(dest), bytes=dest.stat().st_size, needed=needed))
assert replaced == 6
assert len(files) == 9
available = {Path(row['name']).name for row in files} | {'libc.so', 'libc++.so'}
assert all(set(row['needed']) <= available for row in files)
assert {row['name'] for row in files} == {row['name'] for row in old['files']}
for path, expected in old['reference_files'].items():
    assert digest(Path(path)) == expected
images = json.loads((reports/'baremetal-sdk-original-init-qemu-060/result.json').read_text())['original_images']
for row in images.values():
    assert digest(Path(row['path'])) == row['sha256']
result = dict(files=files, original_images_unchanged=True, reference_files_unchanged=True,
              reference_files=old['reference_files'], platform_abi='std::__h',
              platform_libcxx_replaced=False, mesa_ndk_runtime_scoped=True,
              service_credentials_modified=False, runtime_executed=False, physical_board_test=False,
              source_change='Unchanged traced bridge; coherent six-library softpipe Mesa build',
              replaced_mesa_libraries=replaced, gallium_drivers=['softpipe'])
(report/'result.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
'''

if __name__ == '__main__':
    subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, check=True)
