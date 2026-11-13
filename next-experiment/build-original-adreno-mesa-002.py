"""Fresh MSM build: retain upstream C++ narrowing diagnostics as warnings."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-adreno-mesa-001.py')))['payload']
payload = payload.replace('original-adreno-mesa-001', 'original-adreno-mesa-002')
anchor = "    args.append('-D'+key+'='+value)"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, """    if key == 'cpp_args':
        value += ' -Wno-error=c++11-narrowing'
""" + anchor)
anchor = "'device_accessed': False"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "'compiler_compatibility': 'Clang 19 C++17 narrowing diagnostics retained as warnings; original sources unchanged', " + anchor)
compile(payload, 'original-adreno-mesa-002-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=1200).returncode)
