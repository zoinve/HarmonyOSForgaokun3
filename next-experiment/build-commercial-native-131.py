"""Offline battery-module candidate; no installation, HDI replacement or boot."""
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
    old = '"huawei_gaokun_ec", "ucsi_huawei_gaokun"'
    assert source.count(old) == 1
    source = source.replace(old, '"huawei_gaokun_ec", "huawei_gaokun_battery", "ucsi_huawei_gaokun"', 1)
    anchor = '            (void)probe("bindings-after-modules", bindings, 5);'
    assert source.count(anchor) == 1
    addition = r'''
            char *battery131[] = {"/bin/busybox", "sh", "-c",
                "echo GAOKUN_BATTERY131_BEGIN_READ_ONLY; "
                "for d in /sys/class/power_supply/*; do "
                "[ -d @Q@$d@Q@ ] || continue; echo SUPPLY=$d; "
                "for a in type present capacity status voltage_now current_now temp online; do "
                "[ ! -f @Q@$d/$a@Q@ ] || { echo ATTRIBUTE=$a; /bin/busybox cat @Q@$d/$a@Q@; }; done; done; "
                "echo BATTERY_DRIVER_BINDING; "
                "/bin/busybox ls -ld /sys/bus/auxiliary/devices/huawei_gaokun_ec.psy.0/driver; "
                "echo GAOKUN_BATTERY131_END_NOT_HDI_ACCEPTANCE", NULL};
            (void)probe("battery-real-sysfs-131", battery131, 5);'''
    addition = addition.replace('@Q@', chr(92) + chr(34))
    return source.replace(anchor, anchor + addition, 1)


def main():
    parent = BUILD / 'commercial61-native-130'
    work = BUILD / 'commercial61-native-131'
    report = ROOT / 'reports/commercial61-native-131'
    assert not work.exists() and not report.exists()
    metadata = json.loads((ROOT / 'reports/commercial61-native-130/result.json').read_text())
    for item in metadata['artifacts']:
        assert sha((parent / item['name']).read_bytes()) == item['sha256']
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    before = {name: (mode, data) for name, mode, data in parse(gzip.decompress((parent / 'initrd.img').read_bytes()))}
    modules = [name for name in before if name.endswith('/huawei-gaokun-battery.ko')]
    assert len(modules) == 1, modules
    work.mkdir()
    report.mkdir()
    for item in metadata['artifacts']:
        if item['name'] not in ('init', 'init.c', 'initrd.img'):
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
    overlay = archive(delta)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    result = dict(parent='commercial61-native-130', changed_members=sorted(delta),
                  module_path=modules[0], module_sha256=sha(before[modules[0]][1]),
                  command=command, overlay_bytes=len(overlay), overlay_sha256=sha(overlay),
                  original_composer_seed_runtime_and_modules_unchanged=True,
                  battery_observation_read_only=True, battery_hdi_integrated=False,
                  target_runtime_verified=False, installed=False, rebooted=False)
    (report / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
