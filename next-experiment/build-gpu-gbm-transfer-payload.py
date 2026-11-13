"""Fresh 904: add independent GBM map/unmap transfer comparison, not a service VDI."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
text = (base / 'build-gpu-allocator-probe-payload.py').read_text()
text = text.replace("source = (base / 'payload-900/init.c').read_text()", "source = (base / 'payload-900/init.c').read_text()")
text = text.replace('payload-903', 'payload-904').replace('command-probe-903', 'command-probe-904')
text = text.replace("work=root/'allocator-probe-903'", "work=root/'gbm-transfer-904'")
text = text.replace('for(unsigned i=0;i<2;i++)', 'for(unsigned i=0;i<3;i++)')
text = text.replace('"/system/lib64/lab-softpipe-167/gpu903-buffer-vdi.so"};', '"/system/lib64/lab-softpipe-167/gpu903-buffer-vdi.so","gbm"};')
anchor = "common=[str(cxx),'-O2','-std=c++17','-Wall','-Wextra',*includes]"
assert text.count(anchor) == 1
text = text.replace(anchor, anchor + '''
probe=(local/'gpu-allocator-probe.cpp').read_text()
probe=probe.replace('int main(int argc, char **argv)', '#include "gpu-gbm-transfer-probe.h"\\nint main(int argc, char **argv)')
probe=probe.replace('if (argc != 2) return 1;', 'if (argc != 2) return 1;\\n    if (!strcmp(argv[1], "gbm")) return gpu904_gbm();')
(work/'probe.cpp').write_text(probe)
shutil.copy2(local/'gpu-gbm-transfer-probe.h',work/'gpu-gbm-transfer-probe.h')
''')
text = text.replace("str(local/'gpu-allocator-probe.cpp')", "str(work/'probe.cpp')")
exec(compile(text, str(base/'build-gpu-allocator-probe-payload.py'), 'exec'), {'__file__': str(base/'build-gpu-allocator-probe-payload.py')})
