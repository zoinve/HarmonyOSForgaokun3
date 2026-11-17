"""Move the original DFX call before the proc survey, retaining original services."""
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
    anchor = '"commercial-server-stack104.log"'
    assert original.count(anchor) == 1
    path = '/mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-104/bootstrap-runtime087'
    assert original.count(path) == 5
    return original.replace(anchor, '"commercial-server-stack105.log"', 1).replace(path, path.replace('-104/', '-105/'))


def main():
    work, report = BUILD/'commercial61-native-105', ROOT/'reports/commercial61-native-105'
    assert not work.exists() and not report.exists()
    parent = BUILD/'commercial61-native-104'
    previous = json.loads((ROOT/'reports/commercial61-native-104/result.json').read_text())
    for item in previous['artifacts']:
        assert sha((parent/item['name']).read_bytes()) == item['sha256']
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE/'build-commercial-native-087.py'))['member']
    before = {n: (m, d) for n, m, d in parse(gzip.decompress((parent/'initrd.img').read_bytes()))}
    after = dict(before)
    probe = before['native-target/reference-stack-probe103']
    assert probe[0] == 0o100755 and sha(probe[1]) == 'bc9f14107ebfb682311bf8c714f148df579141bb443a358ff85199cdc443b181'
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
    old_launch = b'/system/bin/sh /commercial-server-stack104.sh &\n'
    new_launch = b'/system/bin/sh /commercial-server-stack105.sh &\n'
    assert before[key][1].count(old_launch) == 1
    after[key] = (before[key][0], before[key][1].replace(old_launch, new_launch, 1))
    observer = (BASE/'commercial-server-stack-105.sh').read_bytes()
    assert observer.index(b'/system/bin/timeout 12 /reference-stack-probe103') < observer.index(b'for task105 in ')
    additions = {'native-target/commercial-server-stack105.sh': (0o100755, observer)}
    assert not set(additions).intersection(before)
    after.update(additions)
    raw = b''.join(pack(n, m, d, i+1) for i, (n, (m, d)) in enumerate(after.items()))
    raw += pack('TRAILER!!!', 0, b'', len(after)+1)
    (work/'initrd.img').open('xb').write(gzip.compress(raw, compresslevel=6, mtime=0))
    previous['artifacts'] = [dict(name=i['name'], bytes=(work/i['name']).stat().st_size,
                                sha256=sha((work/i['name']).read_bytes())) for i in previous['artifacts']]
    previous['server_stack105'] = dict(probe_sha256=sha(probe[1]), observer_sha256=sha(observer),
        outer_sha256=sha(after['init'][1]), early_wrapper_sha256=sha(after['early-hardware093.sh'][1]),
        sole_observation_delta='DFX call before proc survey; explicit call timing markers',
        dedicated_log='commercial-server-stack105.log', exported_log='snapshot075-commercial-server-stack105.log',
        runtime_bootstrap_and_probe_unchanged=True, original_services_identity_network_and_recovery_unchanged=True,
        observation_can_perturb_timing=True, original_images_written=False,
        changed_archive_members=[n for n in before if before[n] != after[n]], added_archive_members=sorted(additions))
    previous['runtime_verified'] = False
    previous['external_runtime_bootstrap'] = {**previous['external_runtime_bootstrap'],
        'runtime_bootstrap_source': previous['external_runtime_bootstrap']['runtime_bootstrap_source'].replace('-104/', '-105/'),
        'runtime_verified': False}
    for folder in (work, report):
        (folder/'result.json').open('x').write(json.dumps(previous, indent=2))
    for name in ('init.c', 'bootstrap-runtime087.c'):
        shutil.copyfile(work/name, report/name)
    (report/'observer105.sh').open('xb').write(observer)
    print(json.dumps(previous['server_stack105'], indent=2))


if __name__ == '__main__':
    main()
