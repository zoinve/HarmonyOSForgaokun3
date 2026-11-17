"""Prepare only runtime directories required by the supplied memory wrapper."""
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
OLD_RUNTIME_PATH = '/mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-105/bootstrap-runtime087'
NEW_RUNTIME_PATH = OLD_RUNTIME_PATH.replace('commercial61-native-105', 'commercial61-native-108')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def runtime_source(original):
    anchor = 'int main(void)\n{'
    assert original.count(anchor) == 1
    source = original.replace(anchor, '#include "commercial-memmgr-prerequisites-108.h"\n\n' + anchor, 1)
    anchor = '    directory("/tmp", 01777);\n'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '    commercial_memmgr108();\n', 1)
    anchor = '    pid_t observer=fork();if(observer<0)fail("commercial observer");\n'
    assert source.count(anchor) == 1
    addition = '''    pid_t memory108=fork();if(memory108<0)fail("memory service observer 108");
    if(!memory108){
        char *const args108[]={"/system/bin/sh","/commercial-memmgr108.sh",NULL};
        char *const env108[]={"PATH=/system/bin/aurora:/system/bin:/vendor/bin","HOME=/",NULL};
        execve(args108[0],args108,env108);_exit(127);
    }
'''
    return source.replace(anchor, addition + anchor, 1)


def outer_source(original, old_hash, new_hash):
    assert original.count(OLD_RUNTIME_PATH) == 5
    assert original.count(old_hash) == 2
    anchor = '"commercial-server-stack107.log"'
    assert original.count(anchor) == 1
    return original.replace(OLD_RUNTIME_PATH, NEW_RUNTIME_PATH).replace(old_hash, new_hash).replace(
        anchor, anchor + ',"commercial-memmgr108.log"', 1)


if __name__ == '__main__':
    work, report = BUILD / 'commercial61-native-108', ROOT / 'reports/commercial61-native-108'
    assert not work.exists() and not report.exists()
    parent = BUILD / 'commercial61-native-107'
    previous = json.loads((ROOT / 'reports/commercial61-native-107/result.json').read_text())
    for item in previous['artifacts']:
        assert sha((parent / item['name']).read_bytes()) == item['sha256']
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    before = {n: (m, d) for n, m, d in parse(gzip.decompress((parent / 'initrd.img').read_bytes()))}
    after = dict(before)
    work.mkdir()
    report.mkdir()
    changed = {'init', 'init.c', 'initrd.img', 'bootstrap-runtime087', 'bootstrap-runtime087.c'}
    for item in previous['artifacts']:
        if item['name'] not in changed:
            shutil.copyfile(parent / item['name'], work / item['name'])
    def compile_program(name, source, core=False):
        (work / (name + '.c')).open('x').write(source)
        command = ['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
                   str(work / (name + '.c')), '-I', str(BASE)]
        if core:
            command.append(str(BASE / 'baremetal-diagnostic-core.c'))
        command += ['-o', str(work / name)]
        run = subprocess.run(command, capture_output=True)
        (report / (name + '.stdout')).open('xb').write(run.stdout)
        (report / (name + '.stderr')).open('xb').write(run.stderr)
        assert run.returncode == 0, run.stderr.decode(errors='replace')
        shutil.copyfile(work / (name + '.c'), report / (name + '.c'))
    compile_program('bootstrap-runtime087', runtime_source((parent / 'bootstrap-runtime087.c').read_text()))
    runtime_hash = sha((work / 'bootstrap-runtime087').read_bytes())
    old_hash = sha((parent / 'bootstrap-runtime087').read_bytes())
    compile_program('init', outer_source((parent / 'init.c').read_text(), old_hash, runtime_hash), core=True)
    after['init'] = (before['init'][0], (work / 'init').read_bytes())
    wrapper = before['early-hardware093.sh'][1]
    assert wrapper.count(sha(before['init'][1]).encode()) == 1
    after['early-hardware093.sh'] = (before['early-hardware093.sh'][0], wrapper.replace(
        sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1))
    observer = (BASE / 'commercial-memmgr-observer-108.sh').read_bytes()
    additions = {'native-target/commercial-memmgr108.sh': (0o100755, observer)}
    assert not set(additions).intersection(before)
    after.update(additions)
    raw = b''.join(pack(n, m, d, i + 1) for i, (n, (m, d)) in enumerate(after.items()))
    raw += pack('TRAILER!!!', 0, b'', len(after) + 1)
    (work / 'initrd.img').open('xb').write(gzip.compress(raw, compresslevel=6, mtime=0))
    previous['artifacts'] = [dict(name=item['name'], bytes=(work / item['name']).stat().st_size,
        sha256=sha((work / item['name']).read_bytes())) for item in previous['artifacts']]
    previous['external_runtime_bootstrap'] = {**previous['external_runtime_bootstrap'],
        'runtime_bootstrap_source': NEW_RUNTIME_PATH, 'runtime_bootstrap_sha256': runtime_hash,
        'runtime_bootstrap_bytes': (work / 'bootstrap-runtime087').stat().st_size,
        'runtime_source_sha256': sha((work / 'bootstrap-runtime087.c').read_bytes()),
        'runtime_verified': False}
    previous['memmgr108'] = dict(parent='commercial61-native-107',
        runtime_path=NEW_RUNTIME_PATH, runtime_sha256=runtime_hash, old_runtime_sha256=old_hash,
        helper_sha256=sha((BASE / 'commercial-memmgr-prerequisites-108.h').read_bytes()),
        observer_sha256=sha(observer), outer_sha256=sha(after['init'][1]),
        early_wrapper_sha256=sha(after['early-hardware093.sh'][1]),
        changed_archive_members=[n for n in before if before[n] != after[n]],
        added_archive_members=sorted(additions), dedicated_log='commercial-memmgr108.log',
        original_wrappers_services_tokens_identity_network_recovery_unchanged=True,
        prior_event_trigger_observer_unchanged=True, directory_scaffold_only=True,
        no_memory_metrics_or_completion_state_created=True, original_images_written=False,
        service_launch_success_not_assumed=True, runtime_verified=False)
    previous['runtime_verified'] = False
    for directory in (work, report):
        (directory / 'result.json').open('x').write(json.dumps(previous, indent=2))
    shutil.copyfile(BASE / 'commercial-memmgr-prerequisites-108.h', report / 'commercial-memmgr-prerequisites-108.h')
    (report / 'observer108.sh').open('xb').write(observer)
    print(json.dumps(previous['memmgr108'], indent=2))
