"""Preserve the original generated data disk after namespace exit, parent 116."""
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
    declaration = 'static void native_original(void)\n'
    assert source.count(declaration) == 1
    source = source.replace(declaration, '#include "oobe-data-snapshot-121.h"\n\n' + declaration, 1)
    anchor = '            if(got==0){\n                dprintf(1,"COMMERCIAL087 target_timeout=1\\n");'
    assert source.count(anchor) == 1
    source = source.replace(anchor, '''            int data121 = -1;
            if(got==0){
                char path121[128];
                snprintf(path121,sizeof(path121),"/proc/%d/root/data",child);
                data121=open(path121,O_RDONLY|O_DIRECTORY|O_CLOEXEC);
            }
''' + anchor, 1)
    anchor = '            dprintf(1,"COMMERCIAL087_TARGET_EXIT pid=%d status=%d\\n",got,state);'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '''
            if(data121>=0){
                if(got==child && WIFSIGNALED(state) && WTERMSIG(state)==SIGKILL)
                    oobe_snapshot121(data121);
                else {close(data121);dprintf(1,"OOBE121_CAPTURE_REFUSED namespace_exit_unproven=1\\n");}
            }else dprintf(1,"OOBE121_CAPTURE_REFUSED data_mount_not_pinned=1\\n");''', 1)
    return source


if __name__ == '__main__':
    work, report = BUILD / 'commercial61-native-121', ROOT / 'reports/commercial61-native-121'
    assert not work.exists() and not report.exists()
    parent = BUILD / 'commercial61-native-116'
    metadata = json.loads((ROOT / 'reports/commercial61-native-116/result.json').read_text())
    for item in metadata['artifacts']:
        assert sha((parent / item['name']).read_bytes()) == item['sha256']
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    before = {n: (mode, data) for n, mode, data in parse(gzip.decompress((parent / 'initrd.img').read_bytes()))}
    after = dict(before)
    outer = adapt((parent / 'init.c').read_text())
    work.mkdir()
    report.mkdir()
    for item in metadata['artifacts']:
        if item['name'] not in ('init', 'init.c', 'initrd.img'):
            (work / item['name']).open('xb').write((parent / item['name']).read_bytes())
    (work / 'init.c').open('x').write(outer)
    compile_result = subprocess.run(['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
        str(work / 'init.c'), '-I', str(BASE), str(BASE / 'baremetal-diagnostic-core.c'), '-o', str(work / 'init')], capture_output=True)
    (report / 'init.stdout').open('xb').write(compile_result.stdout)
    (report / 'init.stderr').open('xb').write(compile_result.stderr)
    assert compile_result.returncode == 0, compile_result.stderr.decode(errors='replace')
    after['init'] = (before['init'][0], (work / 'init').read_bytes())
    wrapper = before['early-hardware093.sh'][1]
    assert wrapper.count(sha(before['init'][1]).encode()) == 1
    after['early-hardware093.sh'] = (before['early-hardware093.sh'][0],
        wrapper.replace(sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1))
    delta = {n: value for n, value in after.items() if value != before.get(n)}
    assert set(delta) == {'init', 'early-hardware093.sh'}
    def archive(entries):
        raw = b''.join(pack(n, mode, data, i + 1) for i, (n, (mode, data)) in enumerate(entries.items()))
        return gzip.compress(raw + pack('TRAILER!!!', 0, b'', len(entries) + 1), compresslevel=6, mtime=0)
    (work / 'initrd.img').open('xb').write(archive(after))
    overlay = archive(delta)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    previous = json.loads((ROOT / 'reports/commercial61-native-116/overlay-result.json').read_text())
    result = dict(bytes=len(overlay), sha256=sha(overlay), members=sorted(delta),
        chain=previous['chain'] + ['commercial61-native-121/initrd.img'],
        shared_parent_overlay_sha256=previous['sha256'], ordered_chain_equals_full_121=True,
        existing_016_overlay_sha256=previous['existing_016_overlay_sha256'],
        original_images_written=False, runtime_verified=False)
    metadata['artifacts'] = [dict(name=i['name'], bytes=(work / i['name']).stat().st_size,
        sha256=sha((work / i['name']).read_bytes())) for i in metadata['artifacts']]
    metadata['oobe121'] = dict(parent='commercial61-native-116', changed_members=sorted(delta),
        runtime_path=metadata['oobe116']['runtime_path'], runtime_sha256=metadata['oobe116']['runtime_sha256'],
        header_sha256=sha((BASE / 'oobe-data-snapshot-121.h').read_bytes()),
        settings_modified=False, snapshot_target_private_only=True, original_runtime_unchanged=True,
        installed=False, target_boot_performed=False)
    metadata['runtime_verified'] = False
    for directory in (work, report):
        (directory / 'result.json').open('x').write(json.dumps(metadata, indent=2))
        (directory / 'overlay-result.json').open('x').write(json.dumps(result, indent=2))
    (report / 'snapshot-header.h').open('xb').write((BASE / 'oobe-data-snapshot-121.h').read_bytes())
    print(json.dumps(metadata['oobe121'], indent=2))
