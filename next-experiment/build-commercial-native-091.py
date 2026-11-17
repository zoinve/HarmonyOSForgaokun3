"""Native original-API probe, with guarded real-firmware serial supply only."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import shutil
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def script091(binary_sha):
    source = (BASE/'commercial-network-refresh-090.sh').read_text()
    anchor = '/system/bin/id\n'
    assert source.count(anchor) == 1
    addition = r'''
printf 'HARDWARE091_BEGIN original_module_hash_guard=1 real_firmware_only=1\n'
hash091=$(/system/bin/sha256sum /native-hardware091 2>/dev/null || :)
module091=$(/system/bin/sha256sum /system/lib64/init/libudidmodule.z.so 2>/dev/null || :)
if [ "$hash091" = "BINARY_SHA  /native-hardware091" ] &&
   [ "$module091" = "322f5cf59d309e4306e59bf47c11e01748c26d1039492c6e05e9afebe8f9e11c  /system/lib64/init/libudidmodule.z.so" ]; then
    /system/bin/timeout 8 /native-hardware091 --supply-physical-serial
    printf 'HARDWARE091_RESULT exit_status=%s success_not_inferred=1\n' "$?"
else
    printf 'HARDWARE091_REFUSED reason=helper_or_original_module_hash no_write_requested=1\n'
fi
printf 'HARDWARE091_END\n'
'''.replace('BINARY_SHA', binary_sha)
    return source.replace(anchor, anchor + addition, 1).encode()


def main():
    work = BUILD/'commercial61-native-091'
    report = ROOT/'reports/commercial61-native-091'
    assert not work.exists() and not report.exists()
    work.mkdir()
    report.mkdir()
    command = [str(BUILD/'window-bridge/toolchain/ohos-cc'), '-Os', '-s', '-Wall', '-Wextra', '-Werror',
               str(BASE/'native-hardware-091.c'), '-ldl', '-o', str(work/'native-hardware091')]
    result = subprocess.run(command, capture_output=True)
    (report/'compile.stdout').open('xb').write(result.stdout)
    (report/'compile.stderr').open('xb').write(result.stderr)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    helper = (work/'native-hardware091').read_bytes()
    assert helper[:6] == b'\x7fELF\x02\x01' and helper[18:20] == b'\xb7\x00'
    dynamic = subprocess.check_output(['readelf', '-dW', str(work/'native-hardware091')])
    assert b'libc.so.6' not in dynamic and b'libstdc++' not in dynamic
    (report/'dynamic.txt').open('xb').write(dynamic)
    subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', str(BASE/'test-native-hardware-091.c'),
                    '-o', str(work/'decision-tests')], check=True)
    tests = subprocess.check_output([str(work/'decision-tests')])
    (report/'decision-tests.stdout').open('xb').write(tests)
    previous = json.loads((ROOT/'reports/commercial61-native-090/result.json').read_text())
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE/'build-commercial-native-087.py'))['member']
    before = {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD/'commercial61-native-090/initrd.img').read_bytes()))}
    after = dict(before)
    key = 'native-target/commercial-desktop077.sh'
    binary = 'native-target/native-hardware091'
    assert binary not in before
    helper_sha = hashlib.sha256(helper).hexdigest()
    after[key] = (before[key][0], script091(helper_sha))
    after[binary] = (0o100755, helper)
    assert {n for n in before if before[n] != after[n]} == {key}
    for item in previous['artifacts']:
        if item['name'] == 'initrd.img':
            continue
        path = BUILD/'commercial61-native-090'/item['name']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
        shutil.copyfile(path, work/item['name'])
    raw = b''.join(pack(n, m, d, i+1) for i, (n, (m, d)) in enumerate(after.items()))
    raw += pack('TRAILER!!!', 0, b'', len(after)+1)
    (work/'initrd.img').open('xb').write(gzip.compress(raw, compresslevel=6, mtime=0))
    names = [i['name'] for i in previous['artifacts']] + ['native-hardware091']
    previous['artifacts'] = [dict(name=n, bytes=(work/n).stat().st_size,
        sha256=hashlib.sha256((work/n).read_bytes()).hexdigest()) for n in names]
    previous['hardware_input_diagnostic'] = dict(helper_sha256=helper_sha,
        source_sha256=hashlib.sha256((BASE/'native-hardware-091.c').read_bytes()).hexdigest(),
        original_module_sha256='322f5cf59d309e4306e59bf47c11e01748c26d1039492c6e05e9afebe8f9e11c',
        no_replacement_udid_algorithm=True, no_existing_identity_overwrite=True,
        firmware_product_chassis_serials_must_match=True, original_product_metadata_must_match_firmware=True,
        original_parameter_permission_checks_retained=True, no_provisioning_changes=True)
    previous['runtime_verified'] = False
    for folder in (work, report):
        (folder/'result.json').open('x').write(json.dumps(previous, indent=2))
    shutil.copyfile(ROOT/'reports/commercial61-native-090/config-provenance.json', report/'config-provenance.json')
    (report/'diagnostic091.sh').open('xb').write(after[key][1])
    print(json.dumps(previous['hardware_input_diagnostic'], indent=2))


if __name__ == '__main__':
    main()
