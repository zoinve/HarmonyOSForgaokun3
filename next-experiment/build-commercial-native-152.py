"""Inspect the original services' private /dev; preserve the working 148 runtime."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def adapt(source):
    anchor = '#include "native-input-usb-148.h"'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '\n#include "native-service-devices-152.h"', 1)
    anchor = '    native_input148_observe("services_sample148");'
    assert source.count(anchor) == 1
    return source.replace(anchor, anchor + '\n    native_service152_observe();', 1)


if __name__ == '__main__':
    parent = BUILD / 'commercial61-native-148'
    work = BUILD / 'commercial61-native-152'
    report = ROOT / 'reports/commercial61-native-152'
    assert not work.exists() and not report.exists()
    metadata = json.loads((ROOT / 'reports/commercial61-native-148/result.json').read_text())
    for row in metadata['artifacts']:
        assert sha((parent / row['name']).read_bytes()) == row['sha256']
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    member = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    def unpack(path):
        return {n: (m, b) for n, m, b in parser(gzip.decompress(path.read_bytes()))}
    def archive(entries):
        raw = b''.join(member(n, m, b, i + 1) for i, (n, (m, b)) in enumerate(entries.items()))
        return gzip.compress(raw + member('TRAILER!!!', 0, b'', len(entries) + 1), compresslevel=6, mtime=0)
    before = unpack(parent / 'initrd.img')
    modules = metadata['inputusb148']['exact_packaged_modules']
    for row in modules.values():
        assert sha(before[row['path']][1]) == row['sha256']
    previous = json.loads((ROOT / 'reports/commercial61-native-148/overlay-result.json').read_text())
    assert sha((parent / 'minimal-overlay.img').read_bytes()) == previous['sha256']
    work.mkdir()
    report.mkdir()
    for row in metadata['artifacts']:
        if row['name'] not in ['init', 'init.c', 'initrd.img']:
            (work / row['name']).open('xb').write((parent / row['name']).read_bytes())
    (work / 'init.c').open('x').write(adapt((parent / 'init.c').read_text()))
    compiled = subprocess.run(['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
        str(work / 'init.c'), '-I', str(BASE), str(BASE / 'baremetal-diagnostic-core.c'), '-o', str(work / 'init')], capture_output=True, timeout=120)
    (report / 'init.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr.decode(errors='replace')
    after = dict(before)
    after['init'] = (before['init'][0], (work / 'init').read_bytes())
    mode, wrapper = before['early-hardware093.sh']
    assert wrapper.count(sha(before['init'][1]).encode()) == 1
    after['early-hardware093.sh'] = (mode, wrapper.replace(sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1))
    delta = {n: v for n, v in after.items() if before.get(n) != v}
    assert set(delta) == {'init', 'early-hardware093.sh'}
    (work / 'initrd.img').open('xb').write(archive(after))
    minimal = unpack(parent / 'minimal-overlay.img')
    minimal.update(delta)
    overlay = archive(minimal)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    assert previous['chain'][-1] == 'commercial61-native-148/initrd.img'
    chain = previous['chain'][:-1] + ['commercial61-native-152/initrd.img']
    metadata['artifacts'] = [dict(name=r['name'], bytes=(work / r['name']).stat().st_size,
                                 sha256=sha((work / r['name']).read_bytes())) for r in metadata['artifacts']]
    metadata['inputusb152'] = dict(source_sha256=sha((work / 'init.c').read_bytes()),
        header_sha256=sha((BASE / 'native-service-devices-152.h').read_bytes()), exact_packaged_modules=modules,
        service_root_sample_interval_seconds=20, read_only=True, permissions_changed=False,
        original_modules_runtime_seed_dtb_services_unchanged=True)
    metadata['runtime_verified'] = False
    overlay_result = dict(bytes=len(overlay), sha256=sha(overlay), members=sorted(minimal), chain=chain,
        changed_from_full_parent=sorted(delta), shared_parent_overlay_sha256=previous['sha256'],
        ordered_chain_equals_full_152=True, existing_016_overlay_sha256=previous['existing_016_overlay_sha256'],
        original_images_written=False, runtime_verified=False)
    for folder in [work, report]:
        (folder / 'result.json').open('x').write(json.dumps(metadata, indent=2))
        (folder / 'overlay-result.json').open('x').write(json.dumps(overlay_result, indent=2))
    print(json.dumps(metadata['inputusb152'], indent=2))
