"""Add bounded enumeration through the unchanged original native libusb."""
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


def adapt_script(source, helper_hash, library_hash):
    anchor = 'unset identity093 hash093\n'
    assert source.count(anchor) == 1
    addition = r'''
(
    count153=0
    while [ "$count153" -lt 60 ]; do
        IFS=' ' read -r uptime153 rest153 < /proc/uptime || exit 1
        seconds153=${uptime153%%.*}
        [ "$seconds153" -lt 60 ] || break
        count153=$((count153+1))
        /system/bin/sleep 1
    done
    if [ "$count153" -ge 60 ]; then
        printf 'USB153_REFUSED reason=admission_timeout\n'
        exit 1
    fi
    helper153=$(/system/bin/sha256sum /native-usb153 2>/dev/null || :)
    library153=$(/system/bin/sha256sum /system/lib64/chipset-sdk-sp/libusb_shared.z.so 2>/dev/null || :)
    if [ "$helper153" = "HELPER_HASH  /native-usb153" ] &&
       [ "$library153" = "LIBRARY_HASH  /system/lib64/chipset-sdk-sp/libusb_shared.z.so" ]; then
        /system/bin/timeout 8 /native-usb153 --enumerate-original-backend
        printf 'USB153_PROBE_RESULT status=%s backend_only=1\n' "$?"
    else
        printf 'USB153_REFUSED reason=helper_or_original_library_hash\n'
    fi
) &
'''.replace('HELPER_HASH', helper_hash).replace('LIBRARY_HASH', library_hash)
    return source.replace(anchor, anchor + addition, 1)


if __name__ == '__main__':
    parent, work = BUILD / 'commercial61-native-152', BUILD / 'commercial61-native-153'
    report = ROOT / 'reports/commercial61-native-153'
    assert not work.exists() and not report.exists()
    metadata = json.loads((ROOT / 'reports/commercial61-native-152/result.json').read_text())
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
    previous = json.loads((ROOT / 'reports/commercial61-native-152/overlay-result.json').read_text())
    assert sha((parent / 'minimal-overlay.img').read_bytes()) == previous['sha256']
    original = json.loads((ROOT / 'reports/usb-implementation-151/result.json').read_text())
    library = next(row for row in original['libraries'] if row['requested'].endswith('/libusb_shared.z.so'))
    assert library['elf_present'] and library['resolved'] == '/system/lib64/chipset-sdk-sp/libusb_shared.z.so'
    work.mkdir()
    report.mkdir()
    for row in metadata['artifacts']:
        if row['name'] != 'initrd.img':
            (work / row['name']).open('xb').write((parent / row['name']).read_bytes())
    command = [str(BUILD / 'window-bridge/toolchain/ohos-cc'), '-Os', '-s', '-Wall', '-Wextra', '-Werror',
               str(BASE / 'native-usb-enumerate-153.c'), '-ldl', '-o', str(work / 'native-usb153')]
    compiled = subprocess.run(command, capture_output=True, timeout=60)
    (report / 'compile.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr.decode(errors='replace')
    helper = (work / 'native-usb153').read_bytes()
    assert helper[:6] == b'\x7fELF\x02\x01' and helper[18:20] == b'\xb7\x00'
    dynamic = subprocess.check_output(['readelf', '-dW', str(work / 'native-usb153')])
    assert b'libc.so.6' not in dynamic and b'libstdc++' not in dynamic
    (report / 'dynamic.txt').open('xb').write(dynamic)
    after = dict(before)
    key = 'native-target/commercial-desktop077.sh'
    after[key] = (before[key][0], adapt_script(before[key][1].decode(), sha(helper), library['sha256']).encode())
    new = 'native-target/native-usb153'
    assert new not in before
    after[new] = (0o100755, helper)
    assert {n for n in before if before[n] != after[n]} == {key}
    assert set(after) - set(before) == {new}
    (work / 'initrd.img').open('xb').write(archive(after))
    minimal = unpack(parent / 'minimal-overlay.img')
    minimal.update({key: after[key], new: after[new]})
    overlay = archive(minimal)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    assert previous['chain'][-1] == 'commercial61-native-152/initrd.img'
    chain = previous['chain'][:-1] + ['commercial61-native-153/initrd.img']
    metadata['artifacts'] = [dict(name=row['name'], bytes=(work / row['name']).stat().st_size,
        sha256=sha((work / row['name']).read_bytes())) for row in metadata['artifacts']]
    metadata['artifacts'].append(dict(name='native-usb153', bytes=len(helper), sha256=sha(helper)))
    metadata['usb153'] = dict(helper_sha256=sha(helper), source_sha256=sha((BASE / 'native-usb-enumerate-153.c').read_bytes()),
        original_library_sha256=library['sha256'], script_sha256=sha(after[key][1]), command=command,
        original_init_runtime_services_modules_dtb_unchanged=True, transfer_configuration_identity_apis_used=False,
        target_uptime_seconds=60, probe_timeout_seconds=8, backend_only=True, target_runtime_verified=False)
    metadata['runtime_verified'] = False
    overlay_result = dict(bytes=len(overlay), sha256=sha(overlay), members=sorted(minimal), chain=chain,
        changed_from_full_parent=[key], added_from_full_parent=[new], shared_parent_overlay_sha256=previous['sha256'],
        ordered_chain_equals_full_153=True, existing_016_overlay_sha256=previous['existing_016_overlay_sha256'],
        original_images_written=False, runtime_verified=False)
    for folder in [work, report]:
        (folder / 'result.json').open('x').write(json.dumps(metadata, indent=2))
        (folder / 'overlay-result.json').open('x').write(json.dumps(overlay_result, indent=2))
    print(json.dumps(metadata['usb153'], indent=2))
