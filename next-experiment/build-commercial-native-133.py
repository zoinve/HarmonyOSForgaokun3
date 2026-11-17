"""Keep original Battery HDI; register its real sysfs node and observe readings."""
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
    old = 'if(probe("oobe-seed-load123",seed123,12))okay=0;'
    assert source.count(old) == 1
    source = source.replace(old, 'if(probe("oobe-seed-load123",seed123,36))okay=0;', 1)
    anchor = '#include "native-backlight-permissions-130.h"'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '\n#include "native-driver-observer-133.h"', 1)
    anchor = '    network081_kmsg();\n    network081_netifs();'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '\n    native_driver_observer133("services_sample");', 1)
    anchor = '    if(okay && native_backlight_permissions130()){'
    assert source.count(anchor) == 1
    return source.replace(anchor, '    if(okay)native_driver_observer133("before_services");\n' + anchor, 1)


if __name__ == '__main__':
    work = BUILD / 'commercial61-native-133'
    parent = BUILD / 'commercial61-native-131'
    report = ROOT / 'reports/commercial61-native-133'
    assert not work.exists() and not report.exists()
    metadata = json.loads((ROOT / 'reports/commercial61-native-131/deployment-manifest.json').read_text())
    for item in metadata['artifacts']:
        assert sha((parent / item['name']).read_bytes()) == item['sha256']
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    before = {name: (mode, data) for name, mode, data in parse(gzip.decompress((parent / 'initrd.img').read_bytes()))}
    module = json.loads((ROOT / 'reports/commercial-battery-module-132/result.json').read_text())
    library = Path(module['module']).read_bytes()
    assert sha(library) == module['module_sha256']
    module_path = json.loads((ROOT / 'reports/commercial61-native-131/result.json').read_text())['module_path']
    work.mkdir()
    report.mkdir()
    for item in metadata['artifacts']:
        if item['name'] not in ['init', 'init.c', 'initrd.img']:
            (work / item['name']).open('xb').write((parent / item['name']).read_bytes())
    (work / 'init.c').open('x').write(adapt((parent / 'init.c').read_text()))
    command = ['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
               str(work / 'init.c'), '-I', str(BASE), str(BASE / 'baremetal-diagnostic-core.c'), '-o', str(work / 'init')]
    compiled = subprocess.run(command, capture_output=True, timeout=120)
    (report / 'init.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr.decode(errors='replace')
    after = dict(before)
    after['init'] = (before['init'][0], (work / 'init').read_bytes())
    mode, wrapper = before['early-hardware093.sh']
    assert wrapper.count(sha(before['init'][1]).encode()) == 1
    after['early-hardware093.sh'] = (mode, wrapper.replace(sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1))
    after[module_path] = (before[module_path][0], library)
    delta = {name: value for name, value in after.items() if before.get(name) != value}
    assert set(delta) == {'init', 'early-hardware093.sh', module_path}
    def archive(entries):
        raw = b''.join(pack(name, mode, data, index + 1) for index, (name, (mode, data)) in enumerate(entries.items()))
        return gzip.compress(raw + pack('TRAILER!!!', 0, b'', len(entries) + 1), compresslevel=6, mtime=0)
    (work / 'initrd.img').open('xb').write(archive(after))
    # Replacing fully shadowed 131 avoids growing the EFI command line again.
    previous = json.loads((ROOT / 'reports/commercial61-native-131/overlay-result.json').read_text())
    assert previous['members'] == ['early-hardware093.sh', 'init']
    chain = previous['chain'][:-1] + ['commercial61-native-133/initrd.img']
    assert previous['chain'][-1] == 'commercial61-native-131/initrd.img'
    overlay = archive(delta)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    metadata['artifacts'] = [dict(name=row['name'], bytes=(work / row['name']).stat().st_size,
                                 sha256=sha((work / row['name']).read_bytes())) for row in metadata['artifacts']]
    metadata['driver133'] = dict(module_path=module_path, module_sha256=module['module_sha256'],
                               real_sysfs_registration_name='battery', seed_copy_budget_seconds=36,
                               seed_contents_and_hash_unchanged=True, original_battery_hdi_unchanged=True,
                               observer_read_only=True, original_composer_and_runtime_unchanged=True,
                               battery_hdi_runtime_verified=False, battery_ui_verified=False)
    metadata['runtime_verified'] = False
    overlay_result = dict(bytes=len(overlay), sha256=sha(overlay), members=sorted(delta), chain=chain,
                          shared_parent_overlay_sha256=previous['sha256'], ordered_chain_equals_full_133=True,
                          existing_016_overlay_sha256=previous['existing_016_overlay_sha256'],
                          original_images_written=False, runtime_verified=False)
    for folder in [work, report]:
        (folder / 'result.json').open('x').write(json.dumps(metadata, indent=2))
        (folder / 'overlay-result.json').open('x').write(json.dumps(overlay_result, indent=2))
    print(json.dumps(metadata['driver133'], indent=2))
