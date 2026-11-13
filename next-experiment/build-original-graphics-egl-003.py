"""Compile a reversibly traced bridge; originals and actual delegation unchanged."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-egl-002.py')))['payload']
payload = payload.replace('original-graphics-egl-002', 'original-graphics-egl-003')
anchor = "cpp=work/'egl_window_bridge.cpp';cpp.write_text(adapted)"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, """import runpy
trace=runpy.run_path(str(project/'next-experiment/original-graphics-egl-trace-001.py'))
traced=trace['adapt'](adapted)
assert trace['strip_trace'](traced)==adapted
cpp=work/'egl_window_bridge.cpp';cpp.write_text(traced)""")
payload = payload.replace('One absolute Mesa dlopen path only; reference source unmodified',
                          'One Mesa path plus reversible bounded EGL result tracing; reference source unmodified')
compile(payload, 'original-graphics-egl-003', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=240).returncode)
