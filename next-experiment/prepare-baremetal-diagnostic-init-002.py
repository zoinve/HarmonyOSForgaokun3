"""Package the explicit PCIe PHY bootstrap in fresh 002 directories, offline only."""
from pathlib import Path
import ast
import hashlib
import runpy


def launcher_source():
    base = Path(__file__).resolve().parent
    generate = runpy.run_path(str(base / 'baremetal-diagnostic-storage-002.py'))['build_source']
    candidate = generate((base / 'baremetal-diagnostic-init.c').read_text())
    source = (base / 'prepare-baremetal-diagnostic-init-001.py').read_text()
    source = source.replace('baremetal-diagnostic-init-001', 'baremetal-diagnostic-init-002')
    source = source.replace('native-diagnostic-init-001', 'native-diagnostic-init-002')
    anchor = "work = '/home/zoinve/harmony-virgl-883/baremetal-diagnostic-init-002'"
    assert source.count(anchor) == 1
    source = source.replace(anchor,
        "hashes['baremetal-diagnostic-init.c'] = " + repr(hashlib.sha256(candidate.encode()).hexdigest()) + '\n' + anchor)
    anchor = 'data=(base/name).read_bytes(); assert hashlib.sha256(data).hexdigest()==digest'
    assert source.count(anchor) == 1
    source = source.replace(anchor,
        "data=" + repr(candidate.encode()) + " if name=='baremetal-diagnostic-init.c' else (base/name).read_bytes(); assert hashlib.sha256(data).hexdigest()==digest")
    # The parent's payload adds only /init to the same immutable base. It runs
    # the result outside PID1 solely to verify refusal; never run it as PID1.
    ast.parse(source)
    return source


if __name__ == '__main__':
    exec(compile(launcher_source(), 'diagnostic-002-generated', 'exec'))
