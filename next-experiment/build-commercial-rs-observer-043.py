"""Build actual Binder-boundary observation using the original commercial runtime."""
from pathlib import Path
import hashlib
import json
import runpy
import shutil
import subprocess

base = Path(__file__).resolve().parents[1]
root = Path('/home/zoinve/harmony-virgl-883')
work = root / 'commercial-rs-observer-043'
local = base / 'reports/commercial-rs-observer-043'
assert not work.exists() and not local.exists()
work.mkdir()
local.mkdir()
source = (base / 'next-experiment/commercial-rs-observer-042.cpp').read_text().replace('042', '043')
source += '\n' + (base / 'next-experiment/commercial-binder-observer-043.h').read_text()
path = work / 'commercial-rs-observer-043.cpp'
path.write_text(source)
previous = json.loads((base / 'reports/commercial-rs-observer-042-r3/result.json').read_text())
command = previous['command'][:previous['command'].index('-shared')]
runtime = root / 'commercial-graphics-014/runtime'
binary = work / 'libcommercial_rs_observer043.so'
command += ['-shared', '-fPIC', '-O2', '-std=c++17', '-Wall', '-Wextra', '-Werror', str(path),
            str(runtime / 'libc++.so'), str(runtime / 'libc.so'), '-ldl', '-pthread',
            '-Wl,--no-undefined', '-Wl,-soname,libcommercial_rs_observer043.so', '-o', str(binary)]
with (work / 'build.stdout').open('xb') as out, (work / 'build.stderr').open('xb') as err:
    subprocess.run(command, stdout=out, stderr=err, check=True, timeout=120)
exports = subprocess.check_output(['aarch64-linux-gnu-nm', '-D', '--defined-only', str(binary)], text=True)
assert any(line.split()[-1] == 'ioctl' for line in exports.splitlines())
expected = {item['symbol'] for item in previous['observed_original_symbols']}
actual = {line.split()[-1] for line in exports.splitlines() if line.split()[-1].startswith('_ZN4OHOS5Rosen')}
assert actual == expected
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result = dict(command=command, library_sha256=sha(binary), library_bytes=binary.stat().st_size,
              source_sha256=sha(path), public_binder_uapi=True, original_calls_forwarded=True,
              request_payloads_modified=False, security_checks_modified=False,
              ioctl_stage_log_limit_per_process=264, target_verified=False, desktop_verified=False)
(work / 'result.json').write_text(json.dumps(result, indent=2))
original = runpy.run_path(str(base / 'next-experiment/commercial-reference-namespace-036.py'))['source']()
old = 'static const char *kPreload = "libappspawn_helper.z.so";'
assert original.count(old) == 1
namespace = original.replace(old, 'static const char *kPreload = "libappspawn_helper.z.so:/system/lib64/libcommercial_rs_observer043.so";', 1)
assert namespace[namespace.index('int main('):] == original[original.index('int main('):]
ns = work / 'namespace-observer043.c'
ns.write_text(namespace)
nsbinary = work / 'appspawn-reference-namespace'
subprocess.run(['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror', str(ns), '-o', str(nsbinary)], check=True, timeout=60)
nsresult = dict(source_sha256=sha(ns), binary_sha256=sha(nsbinary), reference_main_unchanged=True,
                original_appspawn_helper_retained=True, identity_sandbox_argv_unchanged=True)
(work / 'namespace-result.json').write_text(json.dumps(nsresult, indent=2))
for name in [path.name, ns.name, 'result.json', 'namespace-result.json', 'build.stdout', 'build.stderr']:
    shutil.copyfile(work / name, local / name)
print(json.dumps(result, indent=2))
