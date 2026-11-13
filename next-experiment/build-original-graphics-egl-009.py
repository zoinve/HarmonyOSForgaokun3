"""Compile real-current tracing against the coherent software Mesa closure."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-egl-007.py')))['payload']
payload = payload.replace('original-graphics-egl-007', 'original-graphics-egl-009')
payload = payload.replace('original-graphics-egl-trace-005.py', 'original-graphics-egl-trace-006.py')
anchor = "source=(ref/'egl_window_bridge.cpp').read_text()"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, '''software=json.loads((project/'reports/original-softpipe-001/result.json').read_text())
assert software['gallium_drivers']==['softpipe'] and software['original_build_unchanged']
assert len(software['files'])==6
for row in software['files']:
 replacement=Path(row['path'])
 assert sha(replacement)==row['sha256'] and replacement.stat().st_size==row['bytes']
 destination=mesa/row['name']
 assert destination.is_file() and not destination.is_symlink()
 destination.write_bytes(replacement.read_bytes())
 assert sha(destination)==row['sha256']
''' + anchor)
payload = payload.replace('result=dict(files=files,', "result=dict(gallium_drivers=['softpipe'],replaced_mesa_libraries=6,files=files,")
compile(payload, 'original-graphics-egl-009', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=240).returncode)
