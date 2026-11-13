"""Read-only artifact verification and reconciliation; execute no target code."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib, json, re, struct, subprocess
root = Path('/home/zoinve/harmony-virgl-883')
project = Path('/mnt/d/lab/HarmonyOSForMatebookego')
work = root/'original-adreno-mesa-002'
report = project/'reports/original-adreno-mesa-002-independent'
assert not report.exists(), 'Preserve completed independent audits'
report.mkdir()
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
manifest = work/'result.json'
d = json.loads(manifest.read_text())
assert json.loads((project/'reports/original-adreno-mesa-002/result.json').read_text()) == d
assert d['gallium_drivers'] == ['freedreno'] and d['freedreno_kmds'] == ['msm']
assert d['allow_kcmp'] == 'enabled'
assert not any(d[k] for k in ('driver_runtime_verified','physical_board_test','installed','device_accessed','kernel_modesetting_attempted'))
assert all(c['returncode'] == 0 for c in d['commands'])
options = json.loads((work/'build/meson-info/intro-buildoptions.json').read_text())
values = {r['name']:r['value'] for r in options}
assert values['gallium-drivers'] == ['freedreno'] and values['freedreno-kmds'] == ['msm']
assert values['allow-kcmp'] == 'enabled'
compile_db = json.loads((work/'build/compile_commands.json').read_text())
assert any('-DALLOW_KCMP' in r['command'] and '-DHAVE_FREEDRENO' in r['command'] for r in compile_db)
assert all(sha(Path(p)) == h for p,h in d['source_guards'].items())
files = []
assert len(d['files']) == 6 and len({r['name'] for r in d['files']}) == 6
for index,row in enumerate(d['files']):
    p = Path(row['path'])
    assert p.is_relative_to(work/'bundle') and p.is_file() and not p.is_symlink()
    assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256']
    body = p.read_bytes()
    assert body[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<HH',body,16) == (3,183)
    dynamic = subprocess.check_output(['llvm-readelf-19','-dW',str(p)],text=True)
    (report/f'{index}.dynamic.txt').write_text(dynamic)
    needed = re.findall(r'\(NEEDED\).*?\[(.*?)\]',dynamic)
    assert not set(needed) & {'libc.so.6','libstdc++.so.6','libgcc_s.so.1'}
    files.append(dict(**row,needed=needed))
gallium = next(r for r in d['files'] if r['name']=='libgallium-25.0.1.so')
symbols = subprocess.check_output(['llvm-nm-19','-C',gallium['path']],text=True)
for name in ('fd_device_new','fd_screen_create','os_same_file_description'):
    assert re.search(r'\b'+name+r'$',symbols,re.M), name
(report/'gallium.symbols.txt').write_text(symbols)
images = json.loads((project/'reports/baremetal-sdk-original-init-qemu-099/result.json').read_text())['original_images']
assert len(images) == 3
for row in images.values():
    p = Path(row['path'])
    assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256']
prior = project/'reports/baremetal-native-trial-012-collected'
collection = json.loads((prior/'collection.json').read_text())
assert len(collection['files']) == 378
for row in collection['files']:
    p = prior/row['path']
    assert p.is_relative_to(prior) and p.stat().st_size == row['bytes'] and sha(p)==row['sha256']
existing = project/'reports/native-original-graphics-boot-041/runtime-evidence'
retrieval = json.loads((existing/'retrieval-manifest.json').read_text())
assert len(retrieval['files']) == 71
for name,row in retrieval['files'].items():
    assert Path(name).name == name
    p = existing/'raw'/name
    assert not p.is_symlink() and p.stat().st_size == row['bytes'] and sha(p)==row['sha256']
result = dict(files_verified=files,source_guards_verified=len(d['source_guards']),
    actual_driver_options={k:values[k] for k in ('gallium-drivers','freedreno-kmds','allow-kcmp')},
    freedreno_and_kcmp_compile_flags_verified=True,original_sdk_images_unchanged=True,
    prior_native_trial012_files_verified=378,existing_native041_raw_files_verified=71,
    existing_native041_is_not_a_new_run=True,manifest_sha256=sha(manifest),
    runtime_dependency_closure_verified=False,driver_runtime_verified=False,
    target_code_executed=False,device_accessed=False,installed=False)
with (report/'result.json').open('x') as f: json.dump(result,f,indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='files_verified'},indent=2))
'''

if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],
                                   input=payload,text=True,timeout=240).returncode)
