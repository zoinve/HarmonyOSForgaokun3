"""Append a tiny hash-checked loader; preserve every existing EFI payload."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import shlex
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')
HELPER_SOURCE = '/mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-helper-161/live-debug161'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def helper_source161():
    source = runpy.run_path(str(BASE / 'build-commercial-native-159.py'))['helper_source159']()
    source = source.replace('LIVE159','LIVE161')
    anchor = '#include "live-debug-discovery-159.h"'
    assert source.count(anchor) == 1
    source = source.replace(anchor,anchor + '\n#include "live-debug-storage-161.h"',1)
    start = source.index('static int bind_log159(')
    end = source.index('static int address159(',start)
    source = source[:start] + source[end:]
    old = '    if (bind_log159(196,ROOT159 "/logs/hilog") || bind_log159(197,ROOT159 "/logs/native") || key_copy159()) return 93;'
    new = '    if (live_storage161_bind(196,ROOT159 "/logs/hilog",1) || live_storage161_bind(197,ROOT159 "/logs/native",2) || live_storage161_key(KEY159,ROOT159 "/etc/diag/host_ed25519")) return 93;'
    assert source.count(old) == 1
    return source.replace(old,new,1)


def loader161(digest, source=HELPER_SOURCE, destination='/run/live-debug161'):
    assert len(digest) == 64 and set(digest) <= set('0123456789abcdef')
    return '''#!/bin/busybox sh
set -eu
test "$#" = 2 && test "$1" = --native-live159 || exit 77
case "$2" in ''|*[!0-9]*|0*) exit 77;; esac
source=SOURCE_PATH
destination=DESTINATION_PATH
test -f /proc/self/fd/196 && test -f /proc/self/fd/197 || {
    echo 'LIVE161_LOADER_REFUSED inherited_log_fds=1'; exit 104;
}
test -f "$source" && test ! -L "$source" || exit 105
test ! -e "$destination" && test ! -L "$destination" || exit 106
test "$(/bin/busybox sha256sum "$source")" = "DIGEST  $source" || exit 107
/bin/busybox cp "$source" "$destination"
/bin/busybox chmod 0500 "$destination"
test "$(/bin/busybox sha256sum "$destination")" = "DIGEST  $destination" || exit 108
echo 'LIVE161_LOADER_READY source_hash_verified=1 ram_hash_verified=1 inherited_log_fds_present=1'
exec "$destination" "$@"
'''.replace('SOURCE_PATH',shlex.quote(source)).replace('DESTINATION_PATH',shlex.quote(destination)).replace('DIGEST',digest)


if __name__ == '__main__':
    parent, work = BUILD / 'commercial61-native-159', BUILD / 'commercial61-native-161'
    report = ROOT / 'reports/commercial61-native-161'
    assert not work.exists() and not report.exists(), 'preserve numbered evidence'
    metadata = json.loads((ROOT / 'reports/commercial61-native-159/result.json').read_text())
    for row in metadata['artifacts']:
        assert sha((parent / row['name']).read_bytes()) == row['sha256']
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    member = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    before = {n:(m,b) for n,m,b in parser(gzip.decompress((parent / 'initrd.img').read_bytes()))}
    previous = json.loads((ROOT / 'reports/commercial61-native-159/overlay-result.json').read_text())
    work.mkdir();report.mkdir()
    for row in metadata['artifacts']:
        if row['name'] not in ['initrd.img','live-debug159']:
            (work / row['name']).open('xb').write((parent / row['name']).read_bytes())
    source = helper_source161()
    (work / 'live-debug-launcher-161.c').open('x').write(source)
    compiled = subprocess.run(['aarch64-linux-gnu-gcc','-static','-Os','-s','-Wall','-Wextra','-Werror','-I',str(BASE),
        str(work / 'live-debug-launcher-161.c'),'-o',str(work / 'live-debug161')],capture_output=True,timeout=60)
    (report / 'helper-compile.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode == 0,compiled.stderr.decode()
    binary_hash = sha((work / 'live-debug161').read_bytes())
    loader = loader161(binary_hash).encode()
    (work / 'live-debug159').open('xb').write(loader)
    after = dict(before)
    after['live-debug159'] = (before['live-debug159'][0],loader)
    assert {name for name in before if before[name] != after[name]} == {'live-debug159'}
    def archive(entries):
        raw = b''.join(member(n,m,b,i+1) for i,(n,(m,b)) in enumerate(entries.items()))
        return gzip.compress(raw + member('TRAILER!!!',0,b'',len(entries)+1),compresslevel=6,mtime=0)
    (work / 'initrd.img').open('xb').write(archive(after))
    overlay = archive({'live-debug159':after['live-debug159']})
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    assert len(overlay) < 4096
    chain = previous['chain'] + ['commercial61-native-161/initrd.img']
    assert len(chain) == 29
    metadata['artifacts'] = [dict(name=row['name'],bytes=(work / row['name']).stat().st_size,
        sha256=sha((work / row['name']).read_bytes())) for row in metadata['artifacts']]
    metadata['artifacts'].append(dict(name='live-debug161',bytes=(work / 'live-debug161').stat().st_size,sha256=binary_hash))
    metadata['live161'] = dict(helper_sha256=binary_hash,helper_source_sha256=sha(source.encode()),
        storage_header_sha256=sha((BASE / 'live-debug-storage-161.h').read_bytes()),loader_sha256=sha(loader),
        inherited_init_and_original_services_unchanged=True,inherited_live159_optin_and_log_fds=True,
        helper_staged_on_ubuntu_not_esp=True,hash_checked_ram_copy=True,private_keys_in_overlay=False,
        native_live_connection_verified=False)
    metadata['runtime_verified'] = False
    overlay_result = dict(bytes=len(overlay),sha256=sha(overlay),members=['live-debug159'],chain=chain,
        changed_from_full_parent=['live-debug159'],shared_parent_overlay_sha256=previous['sha256'],
        ordered_chain_equals_full_161=True,existing_016_overlay_sha256=previous['existing_016_overlay_sha256'],
        original_images_written=False,runtime_verified=False)
    for folder in [work,report]:
        (folder / 'result.json').open('x').write(json.dumps(metadata,indent=2))
        (folder / 'overlay-result.json').open('x').write(json.dumps(overlay_result,indent=2))
    print(json.dumps(dict(details=metadata['live161'],overlay=overlay_result),indent=2))
