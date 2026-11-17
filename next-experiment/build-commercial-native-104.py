"""Add one original DFX server capture and an independently exported log."""
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


def sha(body):
    return hashlib.sha256(body).hexdigest()


def outer_source(original):
    anchor = '"native-layout086-100.json","native-layout086-130.json"'
    assert original.count(anchor) == 1
    path = '/mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-101/bootstrap-runtime087'
    assert original.count(path) == 5
    return original.replace(anchor, anchor+',"commercial-server-stack104.log"', 1).replace(path, path.replace('-101/', '-104/'))


def main():
    work, report = BUILD/'commercial61-native-104', ROOT/'reports/commercial61-native-104'
    assert not work.exists() and not report.exists()
    parent = BUILD/'commercial61-native-101'
    previous = json.loads((ROOT/'reports/commercial61-native-101/result.json').read_text())
    probe_manifest = json.loads((ROOT/'reports/reference-stack-probe-103/result.json').read_text())
    load = json.loads((ROOT/'reports/reference-stack-probe-103/load-tests.json').read_text())
    assert load['all_invalid_pid_cases_return_2'] and load['no_process_dump_requested']
    probe = (BUILD/'reference-stack-probe-103/app-stack-probe').read_bytes()
    assert sha(probe) == probe_manifest['probe_sha256'] == 'bc9f14107ebfb682311bf8c714f148df579141bb443a358ff85199cdc443b181'
    for item in previous['artifacts']:
        assert sha((parent/item['name']).read_bytes()) == item['sha256']
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE/'build-commercial-native-087.py'))['member']
    before = {n: (m, d) for n, m, d in parse(gzip.decompress((parent/'initrd.img').read_bytes()))}
    after = dict(before)
    work.mkdir()
    report.mkdir()
    for item in previous['artifacts']:
        if item['name'] not in ('init', 'init.c', 'initrd.img'):
            shutil.copyfile(parent/item['name'], work/item['name'])
    outer = outer_source((parent/'init.c').read_text())
    (work/'init.c').open('x').write(outer)
    command = ['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
               str(work/'init.c'), '-I', str(BASE), str(BASE/'baremetal-diagnostic-core.c'), '-o', str(work/'init')]
    compiled = subprocess.run(command, capture_output=True)
    (report/'init.stdout').open('xb').write(compiled.stdout)
    (report/'init.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr.decode(errors='replace')
    wrapper = before['early-hardware093.sh'][1]
    assert wrapper.count(sha(before['init'][1]).encode()) == 1
    after['init'] = (before['init'][0], (work/'init').read_bytes())
    after['early-hardware093.sh'] = (before['early-hardware093.sh'][0], wrapper.replace(
        sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1))
    key = 'native-target/commercial-desktop077.sh'
    anchor = b'/system/bin/sh /commercial-softbus-observer101.sh &\n'
    assert before[key][1].count(anchor) == 1
    after[key] = (before[key][0], before[key][1].replace(anchor,
        b'/system/bin/sh /commercial-server-stack104.sh &\n'+anchor, 1))
    observer = (BASE/'commercial-server-stack-104.sh').read_bytes()
    additions = {'native-target/reference-stack-probe103': (0o100755, probe),
                 'native-target/commercial-server-stack104.sh': (0o100755, observer)}
    assert not set(additions).intersection(before)
    after.update(additions)
    raw = b''.join(pack(n, m, d, i+1) for i, (n, (m, d)) in enumerate(after.items()))
    raw += pack('TRAILER!!!', 0, b'', len(after)+1)
    (work/'initrd.img').open('xb').write(gzip.compress(raw, compresslevel=6, mtime=0))
    previous['artifacts'] = [dict(name=i['name'], bytes=(work/i['name']).stat().st_size,
                                sha256=sha((work/i['name']).read_bytes())) for i in previous['artifacts']]
    previous['server_stack104'] = dict(probe_sha256=sha(probe), observer_sha256=sha(observer),
        outer_sha256=sha(after['init'][1]), early_wrapper_sha256=sha(after['early-hardware093.sh'][1]),
        sole_observation='one original DFX all-thread server dump five seconds after first guide PID',
        dedicated_log='commercial-server-stack104.log', exported_log='snapshot075-commercial-server-stack104.log',
        runtime_bootstrap_unchanged=True, original_services_identity_network_and_recovery_unchanged=True,
        observation_can_perturb_timing=True, original_images_written=False,
        changed_archive_members=[n for n in before if before[n] != after[n]], added_archive_members=sorted(additions))
    previous['runtime_verified'] = False
    previous['external_runtime_bootstrap'] = {**previous['external_runtime_bootstrap'],
        'runtime_bootstrap_source': previous['external_runtime_bootstrap']['runtime_bootstrap_source'].replace('-101/', '-104/'),
        'runtime_verified': False}
    for folder in (work, report):
        (folder/'result.json').open('x').write(json.dumps(previous, indent=2))
    for name in ('init.c', 'bootstrap-runtime087.c'):
        shutil.copyfile(work/name, report/name)
    (report/'observer104.sh').open('xb').write(observer)
    print(json.dumps(previous['server_stack104'], indent=2))


if __name__ == '__main__':
    main()
