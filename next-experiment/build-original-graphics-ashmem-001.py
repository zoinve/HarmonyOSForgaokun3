"""Build genuine reference ashmem for the isolated VM kernel; never load in host."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib, json, re, shutil, subprocess
root = Path('/home/zoinve/harmony-virgl-883')
out = root / 'original-graphics-ashmem-001'
local = Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/original-graphics-ashmem-001')
out.mkdir(); local.mkdir()
ref = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/kernel/ashmem')
k = root / 'original-graphics-kernel-002/out'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
sources = {n: sha(ref / n) for n in ('hmos_ashmem.c', 'ashmem-uapi.h', 'Makefile')}
guard_paths = [k / '.config', k / 'Module.symvers', k / 'arch/arm64/boot/Image']
before = {str(p): sha(p) for p in guard_paths}
assert before[str(k / 'arch/arm64/boot/Image')] == 'a75433f6f069d6607d3a34c461ae3723287d7ae67d45d72a68c7983f12a50136'
assert 'CONFIG_ARM64_4K_PAGES=y' in (k / '.config').read_text()
release = (k / 'include/config/kernel.release').read_text().strip()
s = (ref / 'hmos_ashmem.c').read_text()
assert s.count('mm_page_size(desc->mm)') == 1
s = s.replace('mm_page_size(desc->mm)', 'PAGE_SIZE')
(out / 'hmos_ashmem.c').write_text(s)
for name in ('ashmem-uapi.h', 'Makefile'):
    (out / name).write_bytes((ref / name).read_bytes())
cmd = ['make', '-C', str(k), 'ARCH=arm64', 'CROSS_COMPILE=aarch64-linux-gnu-', 'M=' + str(out), 'modules']
p = subprocess.run(cmd, text=True, capture_output=True)
(local / 'build.stdout.txt').write_text(p.stdout)
(local / 'build.stderr.txt').write_text(p.stderr)
p.check_returncode()
module = out / 'hmos_ashmem.ko'
modinfo = subprocess.check_output(['readelf', '-p', '.modinfo', str(module)], text=True)
(local / 'modinfo.txt').write_text(modinfo)
assert re.search(r'vermagic=' + re.escape(release) + r'\s', modinfo)
assert {str(p): sha(p) for p in guard_paths} == before
assert all(sha(ref / n) == h for n, h in sources.items())
result = dict(module_path=str(module), module_sha256=sha(module), module_bytes=module.stat().st_size,
              kernel_release=release, kernel_sha256=before[str(k / 'arch/arm64/boot/Image')],
              reference_sources=sources, reference_sources_unchanged=True,
              kernel_inputs_unchanged=True, target_granule=4096,
              source_adaptation='fixed 4-KiB PAGE_SIZE only; reference ashmem operations unchanged',
              loaded_in_host=False, runtime_verified=False, compile_command=cmd)
text = json.dumps(result, indent=2)
(out / 'result.json').write_text(text); (local / 'result.json').write_text(text)
print(text)
'''
compile(payload, 'graphics-ashmem-001-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=300).returncode)
