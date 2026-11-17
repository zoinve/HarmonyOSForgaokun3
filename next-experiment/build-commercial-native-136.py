"""Enable real board audio/Bluetooth kernel modules while retaining native services."""
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
    anchor = '#include "native-driver-observer-133.h"'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '\n#include "native-media-136.h"', 1)
    anchor = '    native_driver_observer133("services_sample");'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '\n    native_media136_observe("services_sample136");', 1)
    anchor = '                network081_netifs();\n                native_original();'
    assert source.count(anchor) == 1
    return source.replace(anchor, '                network081_netifs();\n'
                          '                native_media136_load();\n'
                          '                native_media136_observe("before_services136");\n'
                          '                native_original();', 1)


if __name__ == '__main__':
    work = BUILD / 'commercial61-native-136'
    parent = BUILD / 'commercial61-native-133'
    report = ROOT / 'reports/commercial61-native-136'
    assert not work.exists() and not report.exists()
    metadata = json.loads((ROOT / 'reports/commercial61-native-133/result.json').read_text())
    for item in metadata['artifacts']:
        assert sha((parent / item['name']).read_bytes()) == item['sha256']
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    def members(path):
        return {name: (mode, data) for name, mode, data in parse(gzip.decompress(path.read_bytes()))}
    before = members(parent / 'initrd.img')
    previous = json.loads((ROOT / 'reports/commercial61-native-133/overlay-result.json').read_text())
    previous_delta = members(parent / 'minimal-overlay.img')
    assert set(previous_delta) == set(previous['members'])
    assert sha((parent / 'minimal-overlay.img').read_bytes()) == previous['sha256']
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
    delta = {name: value for name, value in after.items() if before.get(name) != value}
    assert set(delta) == {'init', 'early-hardware093.sh'}
    def archive(entries):
        raw = b''.join(pack(name, mode, data, index + 1) for index, (name, (mode, data)) in enumerate(entries.items()))
        return gzip.compress(raw + pack('TRAILER!!!', 0, b'', len(entries) + 1), compresslevel=6, mtime=0)
    (work / 'initrd.img').open('xb').write(archive(after))
    # Retain 133's real battery module while replacing its shadowed init files.
    previous_delta.update(delta)
    overlay = archive(previous_delta)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    assert previous['chain'][-1] == 'commercial61-native-133/initrd.img'
    chain = previous['chain'][:-1] + ['commercial61-native-136/initrd.img']
    metadata['artifacts'] = [dict(name=row['name'], bytes=(work / row['name']).stat().st_size,
                                 sha256=sha((work / row['name']).read_bytes())) for row in metadata['artifacts']]
    metadata['driver136'] = dict(source_sha256=sha((work / 'init.c').read_bytes()),
                               header_sha256=sha((BASE / 'native-media-136.h').read_bytes()),
                               group_admission_seconds=30, per_probe_seconds=4,
                               real_kernel_module_loading_enabled=True, observation_read_only=True,
                               no_mixer_or_amplifier_register_writes=True,
                               original_services_composer_battery_seed_runtime_and_firmware_unchanged=True,
                               native_audio_hdi_verified=False, audio_playback_verified=False,
                               bluetooth_pairing_verified=False, target_runtime_verified=False)
    metadata['runtime_verified'] = False
    overlay_result = dict(bytes=len(overlay), sha256=sha(overlay), members=sorted(previous_delta), chain=chain,
                          changed_from_full_parent=sorted(delta), shared_parent_overlay_sha256=previous['sha256'],
                          ordered_chain_equals_full_136=True, existing_016_overlay_sha256=previous['existing_016_overlay_sha256'],
                          original_images_written=False, runtime_verified=False)
    for folder in [work, report]:
        (folder / 'result.json').open('x').write(json.dumps(metadata, indent=2))
        (folder / 'overlay-result.json').open('x').write(json.dumps(overlay_result, indent=2))
    print(json.dumps(metadata['driver136'], indent=2))
