"""Report real loader diagnostics and preservation without presuming a fix."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-059.py')))['source']
source = source.replace("number='059', tag='059'", "number='060', tag='059'")
source = source.replace('original-graphics-egl-006', 'original-graphics-egl-007')
anchor = "    collected = BASE / 'reports/baremetal-native-trial-012-collected'"
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    text_rows = sorted(set(re.findall(rb'EGL_TRACE_TEXT pid=(\d+) name=([^\s]+) text=([^\r\n]*)', raw)))
    real_loader_diagnostics = [dict(pid=int(pid), name=name.decode(), text=text.decode(errors='replace'))
                               for pid, name, text in text_rows]
''' + anchor)
source = source.replace('evidence = dict(', 'evidence = dict(real_loader_diagnostics=real_loader_diagnostics, ')
compile(source, 'independent-original-graphics-060', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-060', 'exec'))
