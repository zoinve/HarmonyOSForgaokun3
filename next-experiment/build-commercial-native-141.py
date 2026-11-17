"""Supply exact board topology at current kernel's requested name."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')
TOPOLOGY_SOURCE = 'lib/firmware/qcom/sc8280xp/HUAWEI/gaokun3/audioreach-tplg.bin'
TOPOLOGY_TARGET = 'lib/firmware/qcom/sc8280xp/SC8280XP-HUAWEI-GAOKUN3-tplg.bin'
TOPOLOGY_SHA = 'ee911c748deadc0191af50074b26ad177c8a2e78ff00e9578504b71d5d27b08a'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def adapt(source):
    anchor = '#include "native-media-bindings-139.h"'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '\n#include "native-media-bindings-141.h"', 1)
    anchor = 'native_media136_load();'
    assert source.count(anchor) == 1
    source = source.replace(anchor, 'native_media141_prepare();\n    ' + anchor, 1)
    for stage in ['services_sample136', 'before_services136']:
        anchor = 'native_media139_observe("' + stage + '");'
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + '\n    native_media141_observe("' + stage + '");', 1)
    return source


if __name__ == '__main__':
    parent = BUILD / 'commercial61-native-139'
    work = BUILD / 'commercial61-native-141'
    report = ROOT / 'reports/commercial61-native-141'
    assert not work.exists() and not report.exists()
    metadata = json.loads((ROOT / 'reports/commercial61-native-139/result.json').read_text())
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
    assert TOPOLOGY_TARGET not in before
    assert sha(before[TOPOLOGY_SOURCE][1]) == TOPOLOGY_SHA
    apm = next(body for name, (_, body) in before.items() if name.endswith('/snd-q6apm.ko'))
    assert b'qcom/%s/%s-tplg.bin' in apm
    kernel = BUILD / 'native-binder-kernel-045'
    assert sha((kernel / 'out/sound/soc/qcom/qdsp6/snd-q6apm.ko').read_bytes()) == sha(apm)
    driver = (kernel / 'linux/sound/soc/qcom/sc8280xp.c').read_text()
    assert 'card->driver_name = of_device_get_match_data(dev);' in driver
    assert '"qcom,sc8280xp-sndcard", "sc8280xp"' in driver
    dtb = BUILD / 'native-original-graphics-boot-031/sc8280xp-huawei-gaokun3.dtb'
    dt = subprocess.run([str(kernel / 'out/scripts/dtc/dtc'), '-I', 'dtb', '-O', 'dts', str(dtb)], capture_output=True, check=True).stdout
    assert b'model = "SC8280XP-HUAWEI-GAOKUN3";' in dt
    previous = json.loads((ROOT / 'reports/commercial61-native-139/overlay-result.json').read_text())
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
    after[TOPOLOGY_TARGET] = before[TOPOLOGY_SOURCE]
    after['init'] = (before['init'][0], (work / 'init').read_bytes())
    mode, wrapper = before['early-hardware093.sh']
    assert wrapper.count(sha(before['init'][1]).encode()) == 1
    after['early-hardware093.sh'] = (mode, wrapper.replace(sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1))
    delta = {n: v for n, v in after.items() if before.get(n) != v}
    assert set(delta) == {'init', 'early-hardware093.sh', TOPOLOGY_TARGET}
    (work / 'initrd.img').open('xb').write(archive(after))
    minimal = unpack(parent / 'minimal-overlay.img')
    minimal.update(delta)
    overlay = archive(minimal)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    assert previous['chain'][-1] == 'commercial61-native-139/initrd.img'
    chain = previous['chain'][:-1] + ['commercial61-native-141/initrd.img']
    metadata['artifacts'] = [dict(name=r['name'], bytes=(work / r['name']).stat().st_size,
                                 sha256=sha((work / r['name']).read_bytes())) for r in metadata['artifacts']]
    metadata['driver141'] = dict(source_sha256=sha((work / 'init.c').read_bytes()),
        header_sha256=sha((BASE / 'native-media-bindings-141.h').read_bytes()),
        topology_source=TOPOLOGY_SOURCE, topology_target=TOPOLOGY_TARGET, topology_sha256=TOPOLOGY_SHA,
        topology_bytes_unchanged=True, kernel_and_driver_modules_unchanged=True,
        dtb_sha256=sha(dtb.read_bytes()), original_services_unchanged=True,
        audio_playback_verified=False, runtime_verified=False)
    metadata['runtime_verified'] = False
    overlay_result = dict(bytes=len(overlay), sha256=sha(overlay), members=sorted(minimal), chain=chain,
        changed_from_full_parent=sorted(delta), shared_parent_overlay_sha256=previous['sha256'],
        ordered_chain_equals_full_141=True, existing_016_overlay_sha256=previous['existing_016_overlay_sha256'],
        original_images_written=False, runtime_verified=False)
    for folder in [work, report]:
        (folder / 'result.json').open('x').write(json.dumps(metadata, indent=2))
        (folder / 'overlay-result.json').open('x').write(json.dumps(overlay_result, indent=2))
    print(json.dumps(metadata['driver141'], indent=2))
