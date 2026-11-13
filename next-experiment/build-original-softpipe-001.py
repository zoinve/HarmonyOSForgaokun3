"""Build actual softpipe for the isolated non-3D VM; never install anything."""
import subprocess

payload = r'''
from pathlib import Path
import ast, configparser, hashlib, json, shutil, struct, subprocess, time
root = Path('/home/zoinve/harmony-virgl-883')
work = root / 'original-softpipe-001'
report = Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/original-softpipe-001')
assert not work.exists() and not report.exists()
work.mkdir(exist_ok=False)
report.mkdir(exist_ok=False)
old = root / 'mesa-build'
src = root / 'sources/mesa-mirror-c185b4a7b0ff052f556dff1b3849a9c9c6115640'
cross = root / 'toolchain/ohos-cross.ini'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def code_sections(p):
    b = p.read_bytes()
    assert b[:6] == b'\x7fELF\x02\x01'
    off = struct.unpack_from('<Q', b, 40)[0]
    size, count, index = struct.unpack_from('<HHH', b, 58)
    sections = [struct.unpack_from('<IIQQQQIIQQ', b, off+i*size) for i in range(count)]
    s = sections[index]
    names = b[s[4]:s[4]+s[5]]
    result = {}
    for s in sections:
        name = names[s[0]:].split(b'\0', 1)[0].decode()
        if name in ('.text', '.rodata'):
            result[name] = hashlib.sha256(b[s[4]:s[4]+s[5]]).hexdigest()
    assert len(result) == 2
    return result
old_gallium = old / 'src/gallium/targets/dri/libgallium-25.0.1.so'
packaged_gallium = root / 'original-graphics-egl-007/bundle/harmony-mesa/libgallium-25.0.1.so'
assert digest(packaged_gallium) == 'e2b2800a9471db037e8fdee8edc85c32b04c7e5c031b945aabf383676893f472'
assert code_sections(old_gallium) == code_sections(packaged_gallium)
options = json.loads((old/'meson-info/intro-buildoptions.json').read_text())
assert next(x['value'] for x in options if x['name'] == 'gallium-drivers') == ['virgl']
guards = [old/'build.ninja', old/'meson-private/cmd_line.txt', old_gallium, packaged_gallium, cross,
          src/'meson.build', src/'meson_options.txt', src/'src/gbm/backends/dri/gbm_dri.c']
before = {str(p): digest(p) for p in guards}
config = configparser.ConfigParser(interpolation=None)
config.read(old/'meson-private/cmd_line.txt')
assert ast.literal_eval(config['properties']['cross_file']) == [str(cross)]
args = ['meson', 'setup', str(work/'build'), str(src), '--cross-file', str(cross), '--wrap-mode=nodownload']
for key, value in config['options'].items():
    if key in ('gallium-drivers', 'libdir'): continue
    args.append('-D'+key+'='+value)
args += ['-Dgallium-drivers=softpipe', '-Dlibdir=lib64/harmony-mesa']
commands = []
def run(argv):
    number = len(commands)
    start = time.monotonic()
    with (report/f'{number}.stdout.txt').open('xb') as out, (report/f'{number}.stderr.txt').open('xb') as err:
        p = subprocess.run(argv, stdout=out, stderr=err)
    commands.append(dict(argv=argv, returncode=p.returncode, seconds=time.monotonic()-start))
    (report/'commands.json').write_text(json.dumps(commands, indent=2))
    assert p.returncode == 0, f'command {number} failed; original logs retained'
run(args)
new_options = json.loads((work/'build/meson-info/intro-buildoptions.json').read_text())
assert next(x['value'] for x in new_options if x['name']=='gallium-drivers') == ['softpipe']
run(['ninja', '-C', str(work/'build'), '-j4'])
selected = {'libEGL.so.1':'libEGL.so.1.0.0', 'libGLESv1_CM.so.1':'libGLESv1_CM.so.1.1.0',
            'libGLESv2.so.2':'libGLESv2.so.2.0.0', 'libgbm.so.1':'libgbm.so.1.0.0',
            'libgallium-25.0.1.so':'libgallium-25.0.1.so', 'gbm/dri_gbm.so':'dri_gbm.so'}
files = []
for name, filename in selected.items():
    matches = [p for p in (work/'build/src').rglob(filename) if p.is_file() and not p.is_symlink()]
    assert len(matches)==1, (name, matches)
    dest = work/'bundle'/name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(matches[0], dest)
    run(['patchelf', '--set-rpath', '/system/lib64/harmony-mesa', str(dest)])
    dynamic = subprocess.check_output(['llvm-readelf-19', '-dW', str(dest)], text=True)
    assert all(x not in dynamic for x in ('libc.so.6', 'libstdc++', 'libgcc_s.so'))
    (report/(name.replace('/', '_')+'.dynamic.txt')).write_text(dynamic)
    files.append(dict(name=name, path=str(dest), bytes=dest.stat().st_size, sha256=digest(dest)))
assert all(digest(Path(p))==h for p,h in before.items())
result = {'files': files, 'gallium_drivers': ['softpipe'], 'packaged_virgl_code_sections': code_sections(packaged_gallium),
          'original_build_unchanged': True, 'source_guards': before, 'driver_runtime_verified': False,
          'physical_board_test': False, 'installed': False, 'commands': commands}
(report/'result.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
'''

if __name__ == '__main__':
    subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, check=True)
