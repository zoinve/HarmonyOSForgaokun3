"""Add an optional authenticated diagnostic sidecar without modifying HarmonyOS."""
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


def adapt(source, archive_hash):
    anchor = '#include "native-service-devices-152.h"'
    assert source.count(anchor) == 1
    source = source.replace(anchor,anchor + '\n#define LIVE157_ARCHIVE_SHA "' + archive_hash + '"\n#include "native-live-debug-157.h"',1)
    anchor = '    if(okay)native_driver_observer133("before_services");'
    assert source.count(anchor) == 1
    source = source.replace(anchor,'    if(okay)native_live157_load();\n' + anchor,1)
    anchor = '                if((i==4 || i==7 || i==10 || i==13) && started083){'
    assert source.count(anchor) == 1
    source = source.replace(anchor,'                if(i==4 && started083)native_live157_start(child);\n' + anchor,1)
    anchor = '            snapshot075(child);\n            hw050_tick(child,1);'
    assert source.count(anchor) == 1
    return source.replace(anchor,'            snapshot075(child);\n            native_live157_stop();\n            hw050_tick(child,1);',1)


if __name__ == '__main__':
    parent, work = BUILD / 'commercial61-native-153', BUILD / 'commercial61-native-157'
    report = ROOT / 'reports/commercial61-native-157'
    assert not work.exists() and not report.exists()
    metadata = json.loads((ROOT / 'reports/commercial61-native-153/result.json').read_text())
    for row in metadata['artifacts']:
        assert sha((parent / row['name']).read_bytes()) == row['sha256']
    package = json.loads((ROOT / 'reports/live-debug-inputs-157/result.json').read_text())
    assert not package['private_key_in_archive'] and not package['private_key_read_or_exported']
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    member = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    def unpack(path):
        return {n:(m,b) for n,m,b in parser(gzip.decompress(path.read_bytes()))}
    def archive(entries):
        raw = b''.join(member(n,m,b,i+1) for i,(n,(m,b)) in enumerate(entries.items()))
        return gzip.compress(raw + member('TRAILER!!!',0,b'',len(entries)+1),compresslevel=6,mtime=0)
    before = unpack(parent / 'initrd.img')
    previous = json.loads((ROOT / 'reports/commercial61-native-153/overlay-result.json').read_text())
    assert sha((parent / 'minimal-overlay.img').read_bytes()) == previous['sha256']
    work.mkdir();report.mkdir()
    for row in metadata['artifacts']:
        if row['name'] not in ['init','init.c','initrd.img']:
            (work / row['name']).open('xb').write((parent / row['name']).read_bytes())
    (work / 'init.c').open('x').write(adapt((parent / 'init.c').read_text(),package['sha256']))
    for name, command in [
        ('init',['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(work / 'init.c'),'-I',str(BASE),str(BASE / 'baremetal-diagnostic-core.c'),'-o',str(work / 'init')]),
        ('live-debug157',['aarch64-linux-gnu-gcc','-static','-Os','-s','-Wall','-Wextra','-Werror',str(BASE / 'live-debug-launcher-157.c'),'-o',str(work / 'live-debug157')])]:
        compiled = subprocess.run(command,capture_output=True,timeout=120)
        (report / (name + '.stderr')).open('xb').write(compiled.stderr)
        assert compiled.returncode == 0, compiled.stderr.decode(errors='replace')
    after = dict(before)
    after['init'] = (before['init'][0],(work / 'init').read_bytes())
    mode, wrapper = before['early-hardware093.sh']
    assert wrapper.count(sha(before['init'][1]).encode()) == 1
    after['early-hardware093.sh'] = (mode,wrapper.replace(sha(before['init'][1]).encode(),sha(after['init'][1]).encode(),1))
    assert 'live-debug157' not in before and 'live-debug157-root' not in before
    after['live-debug157'] = (0o100755,(work / 'live-debug157').read_bytes())
    after['live-debug157-root'] = (0o040700,b'')
    delta = {n:v for n,v in after.items() if before.get(n) != v}
    assert set(delta) == {'init','early-hardware093.sh','live-debug157','live-debug157-root'}
    (work / 'initrd.img').open('xb').write(archive(after))
    minimal = unpack(parent / 'minimal-overlay.img');minimal.update(delta)
    overlay = archive(minimal)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    assert previous['chain'][-1] == 'commercial61-native-153/initrd.img'
    chain = previous['chain'][:-1] + ['commercial61-native-157/initrd.img']
    metadata['artifacts'] = [dict(name=row['name'],bytes=(work / row['name']).stat().st_size,sha256=sha((work / row['name']).read_bytes())) for row in metadata['artifacts']]
    metadata['artifacts'].append(dict(name='live-debug157',bytes=(work / 'live-debug157').stat().st_size,sha256=sha((work / 'live-debug157').read_bytes())))
    metadata['live157'] = dict(archive_sha256=package['sha256'],helper_sha256=sha((work / 'live-debug157').read_bytes()),
        helper_source_sha256=sha((BASE / 'live-debug-launcher-157.c').read_bytes()),header_sha256=sha((BASE / 'native-live-debug-157.h').read_bytes()),
        original_runtime_services_seed_modules_kernel_dtb_unchanged=True,private_keys_in_initrd=False,
        separate_root_and_pid_mount_namespaces=True,only_target_network_namespace_joined=True,
        readonly_existing_log_bindings=True,native_live_connection_verified=False,optional_sidecar=True)
    metadata['runtime_verified'] = False
    overlay_result = dict(bytes=len(overlay),sha256=sha(overlay),members=sorted(minimal),chain=chain,
        changed_from_full_parent=sorted(delta),shared_parent_overlay_sha256=previous['sha256'],
        ordered_chain_equals_full_157=True,existing_016_overlay_sha256=previous['existing_016_overlay_sha256'],original_images_written=False,runtime_verified=False)
    for folder in [work,report]:
        (folder / 'result.json').open('x').write(json.dumps(metadata,indent=2))
        (folder / 'overlay-result.json').open('x').write(json.dumps(overlay_result,indent=2))
    print(json.dumps(metadata['live157'],indent=2))
