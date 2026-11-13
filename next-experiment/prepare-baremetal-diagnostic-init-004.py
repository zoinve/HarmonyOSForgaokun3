"""Offline-only 004 packaging with admission budget; no boot or installation."""
from pathlib import Path
import ast
import hashlib
import runpy


def launcher_source():
    base = Path(__file__).resolve().parent
    candidate = (base / 'baremetal-diagnostic-init.c').read_text()
    for version in ('storage-002', 'board-003', 'deadline-004'):
        candidate = runpy.run_path(str(base / ('baremetal-diagnostic-' + version + '.py')))['build_source'](candidate)
    source = (base / 'prepare-baremetal-diagnostic-init-001.py').read_text()
    source = source.replace('baremetal-diagnostic-init-001', 'baremetal-diagnostic-init-004')
    source = source.replace('native-diagnostic-init-001', 'native-diagnostic-init-004')
    anchor = "work = '/home/zoinve/harmony-virgl-883/baremetal-diagnostic-init-004'"
    assert source.count(anchor) == 1
    source = source.replace(anchor,
        "hashes['baremetal-diagnostic-init.c'] = " + repr(hashlib.sha256(candidate.encode()).hexdigest()) + '\n' + anchor)
    anchor = 'data=(base/name).read_bytes(); assert hashlib.sha256(data).hexdigest()==digest'
    assert source.count(anchor) == 1
    source = source.replace(anchor,
        "data=" + repr(candidate.encode()) + " if name=='baremetal-diagnostic-init.c' else (base/name).read_bytes(); assert hashlib.sha256(data).hexdigest()==digest")
    ast.parse(source)
    return source


if __name__ == '__main__':
    exec(compile(launcher_source(), 'diagnostic-004-generated', 'exec'))
