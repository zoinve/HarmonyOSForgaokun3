"""Build a small RAM parameter overlay; preserve the desktop253 runtime."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')


def once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new, 1)


def profile(source):
    source = once(source,
        '    for field in product_serial chassis_serial; do',
        '''    version=$(/bin/busybox cat "$firmware/class/dmi/id/product_version") || return 24
    [ ${#version} -gt 0 ] && [ ${#version} -lt 36 ] || return 24
    case "$version" in *[!A-Za-z0-9_.-]*|default|Default|unknown|Unknown|None|none) return 24 ;; esac
    for field in product_serial chassis_serial; do''')
    source = once(source,
        '        $1 == "const.product.model" { m++ }',
        '''        $1 == "const.product.model" { m++ }
        $1 == "const.product.name" { p++ }
        $1 == "const.product.hardwareversion" { h++ }''')
    source = once(source, 'n == 1 && m == 1 && !bad',
                  'n == 1 && m == 1 && p == 1 && h == 1 && !bad')
    source = once(source,
        '/bin/busybox awk -F= -v model="$model"',
        '/bin/busybox awk -F= -v model="$model" -v name="HUAWEI MateBook E Go" -v version="$version"')
    source = once(source,
        '              $1 == "const.product.model" { print "const.product.model=" model; next }',
        '''              $1 == "const.product.model" { print "const.product.model=" model; next }
              $1 == "const.product.name" { print "const.product.name=" name; next }
              $1 == "const.product.hardwareversion" { print "const.product.hardwareversion=" version; next }''')
    source = once(source, '\n    unset serial chassis digest\n',
                  '\n    unset serial chassis digest version\n')
    return source


if __name__ == '__main__':
    work = BUILD / 'commercial61-native-258'
    report = ROOT / 'reports/commercial61-native-258'
    assert not work.exists() and not report.exists(), 'preserve numbered evidence'
    parser = runpy.run_path(str(ROOT / 'next-experiment/audit-commercial-network-inputs-079.py'))['members']
    member = runpy.run_path(str(ROOT / 'next-experiment/build-commercial-native-087.py'))['member']
    parent = BUILD / 'commercial61-native-253/minimal-overlay.img'
    entries = {n: (m, data) for n, m, data in parser(gzip.decompress(parent.read_bytes()))}
    mode, wrapper = entries['early-hardware093.sh']
    entries['early-hardware093.sh'] = (mode, profile(wrapper.decode()).encode())
    raw = b''.join(member(n, m, data, i + 1) for i, (n, (m, data)) in enumerate(entries.items()))
    overlay = gzip.compress(raw + member('TRAILER!!!', 0, b'', len(entries) + 1), compresslevel=6, mtime=0)
    work.mkdir()
    report.mkdir()
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    (work / 'early-hardware093.sh').open('xb').write(entries['early-hardware093.sh'][1])
    result = dict(parent='253', changed_members=['early-hardware093.sh'],
        display_name='HUAWEI MateBook E Go', model_source='physical DMI product_name',
        hardware_version_source='physical DMI product_version',
        desktop173_runtime_unchanged=True, original_images_modified=False,
        serial_and_udid_logic_unchanged=True, persistent_user_device_name_migration_pending=True,
        installed=False, booted=False, ui_verified=False,
        bytes=len(overlay), sha256=hashlib.sha256(overlay).hexdigest(),
        filesystem_validation_suite_rerun=False, full_image_clone_created=False)
    (report / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
