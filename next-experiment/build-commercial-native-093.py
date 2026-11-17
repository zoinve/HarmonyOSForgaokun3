"""Original init consumes genuine model/serial before its original UDID hook."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import shutil

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')
SERIAL_SHA = 'beb2c73731a4a5df9b7f213455061d27fd07881d876f2e4887feeec4d3fd12a2'


def main():
    work, report = BUILD/'commercial61-native-093', ROOT/'reports/commercial61-native-093'
    assert not work.exists() and not report.exists()
    work.mkdir()
    report.mkdir()
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE/'build-commercial-native-087.py'))['member']
    before = {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD/'commercial61-native-092/initrd.img').read_bytes()))}
    after = dict(before)
    parameter = 'native-target/graphics016/sys_prod/etc/param/hw_defaults.para'
    sha = lambda body: hashlib.sha256(body).hexdigest()
    wrapper = (BASE/'early-hardware-093.sh').read_text().replace('PARAM_SHA', sha(before[parameter][1])).replace(
        'CORE_SHA', sha(before['init'][1])).replace('SERIAL_SHA', SERIAL_SHA).encode()
    after['early-hardware093.sh'] = (0o100755, wrapper)
    key = 'native-target/commercial-desktop077.sh'
    anchor = b'/system/bin/cat /hardware-early092.log\n'
    assert before[key][1].count(anchor) == 1
    privacy = b'''/system/bin/cat /hardware-early093.log
# Only a digest of the original parameter value enters evidence.
identity093=$(/system/bin/param get const.product.devUdid 2>/dev/null)
if [ "$?" -eq 0 ] && [ "${#identity093}" -eq 64 ]; then
    case "$identity093" in
        *[!0-9A-Fa-f]*) printf 'PRIVACY093_ORIGINAL_UDID_HASH unavailable=1\n' ;;
        *) hash093=$(printf '%s\\n' "$identity093" | /system/bin/tr a-f A-F | /system/bin/sha256sum)
           printf 'PRIVACY093_ORIGINAL_UDID_HASH digest=%s normalized_uppercase_newline=1\n' "${hash093%% *}" ;;
    esac
else
    printf 'PRIVACY093_ORIGINAL_UDID_HASH unavailable=1\n'
fi
unset identity093 hash093
'''
    after[key] = (before[key][0], before[key][1].replace(anchor, privacy, 1))
    previous = json.loads((ROOT/'reports/commercial61-native-092/result.json').read_text())
    for item in previous['artifacts']:
        if item['name'] == 'initrd.img':
            continue
        path = BUILD/'commercial61-native-092'/item['name']
        assert sha(path.read_bytes()) == item['sha256']
        shutil.copyfile(path, work/item['name'])
    raw = b''.join(pack(n, m, d, i+1) for i, (n, (m, d)) in enumerate(after.items()))
    raw += pack('TRAILER!!!', 0, b'', len(after)+1)
    (work/'initrd.img').open('xb').write(gzip.compress(raw, compresslevel=6, mtime=0))
    previous['artifacts'] = [dict(name=i['name'], bytes=(work/i['name']).stat().st_size,
        sha256=sha((work/i['name']).read_bytes())) for i in previous['artifacts']]
    previous['early_real_hardware_input'] = dict(wrapper_sha256=sha(wrapper),
        original_parameter_sha256=sha(before[parameter][1]), original_core_sha256=sha(before['init'][1]),
        audited_physical_serial_sha256=SERIAL_SHA, matching_actual_product_and_chassis_required=True,
        ram_model_and_boot_serial_only=True, original_init_owns_udid_calculation=True,
        original_091_identity_guard_binary_unchanged=True, no_identity_algorithm_or_provisioning_changes=True,
        private_ram_parameter_mode=0o600, original_parameter_file_in_archive_unchanged=True)
    previous['runtime_verified'] = False
    for folder in (work, report):
        (folder/'result.json').open('x').write(json.dumps(previous, indent=2))
    (report/'early-hardware093.sh').open('xb').write(wrapper)
    (report/'diagnostic093.sh').open('xb').write(after[key][1])
    shutil.copyfile(ROOT/'reports/commercial61-native-092/config-provenance.json', report/'config-provenance.json')
    print(json.dumps(previous['early_real_hardware_input'], indent=2))


if __name__ == '__main__':
    main()
