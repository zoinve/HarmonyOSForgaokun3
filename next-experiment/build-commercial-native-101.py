"""Mirror only HarmonyMac's explicit SoftBus BLE preload removal in RAM."""
from pathlib import Path
import copy
import gzip
import hashlib
import json
import runpy
import shutil
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')
PRELOAD = '/system/lib64/l410-collaboration/libsoftbus_ble_pc_rsp_preload_v1.so'
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')


def sha(body):
    return hashlib.sha256(body).hexdigest()


def adapt_config(body):
    original = json.loads(body)
    updated = copy.deepcopy(original)
    services = [s for s in updated['services'] if s['name'] == 'softbus_server']
    assert len(services) == 1
    service = services[0]
    entries = service.get('env', [])
    remove = dict(name='LD_PRELOAD', value=PRELOAD)
    assert entries.count(remove) == 1
    service['env'] = [entry for entry in entries if entry != remove]
    restored = copy.deepcopy(updated)
    next(s for s in restored['services'] if s['name'] == 'softbus_server')['env'] = original['services'][updated['services'].index(service)]['env']
    assert restored == original
    return json.dumps(updated, indent=2).encode()+b'\n'


def inner_source(original, digest):
    anchor = '    commercial_copy005("/samgr_standard005.cfg","/run/commercial-system005/upper/etc/init/samgr_standard.cfg",0644);\n'
    assert original.count(anchor) == 1
    extra = ('    commercial_copy005("/softbus-reference101.cfg","/run/commercial-system005/upper/etc/init/softbus_server_musl.cfg",0644);\n'
             '    dprintf(1,"SOFTBUS101_RAM_CONFIG sha256='+digest+' stock_service_permissions_unchanged=1 platform_ble_preload_removed=1\\n");\n')
    return original.replace(anchor, anchor+extra, 1)


def main():
    work, report = BUILD/'commercial61-native-101', ROOT/'reports/commercial61-native-101'
    assert not work.exists() and not report.exists()
    parent = BUILD/'commercial61-native-099'
    previous = json.loads((ROOT/'reports/commercial61-native-099/result.json').read_text())
    for item in previous['artifacts']:
        assert sha((parent/item['name']).read_bytes()) == item['sha256'], item['name']
    raw = subprocess.run(['/usr/sbin/debugfs', '-R', 'cat /system/etc/init/softbus_server_musl.cfg', str(IMAGE)], capture_output=True, check=True).stdout
    audit = json.loads((ROOT/'reports/desktop-dispatch-audit-100/softbus-reference-comparison.json').read_text())
    assert sha(raw) == audit['source_config_sha256']
    config = adapt_config(raw)
    observer = (BASE/'commercial-softbus-observer-101.sh').read_bytes().replace(b'CONFIG_SHA', sha(config).encode())
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE/'build-commercial-native-087.py'))['member']
    before = {n: (m, d) for n, m, d in parse(gzip.decompress((parent/'initrd.img').read_bytes()))}
    after = dict(before)
    work.mkdir()
    report.mkdir()
    for item in previous['artifacts']:
        if item['name'] not in ('init', 'init.c', 'initrd.img', 'bootstrap-runtime087', 'bootstrap-runtime087.c'):
            shutil.copyfile(parent/item['name'], work/item['name'])
    def compile_program(name, text):
        (work/(name+'.c')).open('x').write(text)
        command = ['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror', str(work/(name+'.c')), '-I', str(BASE), '-o', str(work/name)]
        if name == 'init':
            command.insert(-2, str(BASE/'baremetal-diagnostic-core.c'))
        result = subprocess.run(command, capture_output=True)
        (report/(name+'.stdout')).open('xb').write(result.stdout)
        (report/(name+'.stderr')).open('xb').write(result.stderr)
        assert result.returncode == 0, result.stderr.decode(errors='replace')
        shutil.copyfile(work/(name+'.c'), report/(name+'.c'))
    inner = inner_source((parent/'bootstrap-runtime087.c').read_text(), sha(config))
    compile_program('bootstrap-runtime087', inner)
    old_hash = sha((parent/'bootstrap-runtime087').read_bytes())
    runtime_hash = sha((work/'bootstrap-runtime087').read_bytes())
    outer = (parent/'init.c').read_text()
    source = '/mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-087/bootstrap-runtime087'
    assert outer.count(source) == 5 and outer.count(old_hash) == 2
    outer = outer.replace(source, source.replace('commercial61-native-087/', 'commercial61-native-101/')).replace(old_hash, runtime_hash)
    compile_program('init', outer)
    old_core = sha(before['init'][1])
    assert old_core == sha((parent/'init').read_bytes())
    wrapper = before['early-hardware093.sh'][1]
    assert wrapper.count(old_core.encode()) == 1
    after['init'] = (before['init'][0], (work/'init').read_bytes())
    after['early-hardware093.sh'] = (before['early-hardware093.sh'][0], wrapper.replace(old_core.encode(), sha(after['init'][1]).encode(), 1))
    key = 'native-target/commercial-desktop077.sh'
    anchor = b'/system/bin/sh /commercial-reference-observer099.sh &\n'
    assert before[key][1].count(anchor) == 1
    after[key] = (before[key][0], before[key][1].replace(anchor, b'/system/bin/sh /commercial-softbus-observer101.sh &\n'+anchor, 1))
    additions = {'native-target/softbus-reference101.cfg': (0o100644, config),
                 'native-target/commercial-softbus-observer101.sh': (0o100755, observer)}
    assert not set(additions).intersection(before)
    after.update(additions)
    raw_archive = b''.join(pack(n, m, d, i+1) for i, (n, (m, d)) in enumerate(after.items()))
    raw_archive += pack('TRAILER!!!', 0, b'', len(after)+1)
    (work/'initrd.img').open('xb').write(gzip.compress(raw_archive, compresslevel=6, mtime=0))
    (report/'softbus-original.cfg').open('xb').write(raw)
    (report/'softbus-reference101.cfg').open('xb').write(config)
    (report/'observer101.sh').open('xb').write(observer)
    previous['artifacts'] = [dict(name=i['name'], bytes=(work/i['name']).stat().st_size, sha256=sha((work/i['name']).read_bytes())) for i in previous['artifacts']]
    previous['softbus_reference101'] = dict(original_config_sha256=sha(raw), adapted_config_sha256=sha(config),
        observer_sha256=sha(observer), runtime_sha256=runtime_hash, outer_sha256=sha(after['init'][1]),
        early_wrapper_sha256=sha(after['early-hardware093.sh'][1]),
        sole_service_delta='remove exact platform BLE LD_PRELOAD entry',
        original_service_permissions_unchanged=True, original_identity_network_security_and_oobe_recovery_unchanged=True,
        reference_stop_script_unchanged=True, original_images_written=False,
        changed_archive_members=[n for n in before if before[n] != after[n]], added_archive_members=sorted(additions))
    previous['runtime_verified'] = False
    previous['external_runtime_bootstrap'] = {**previous['external_runtime_bootstrap'],
        'runtime_bootstrap_sha256': runtime_hash,
        'runtime_source_sha256': sha(inner.encode()),
        'runtime_bootstrap_bytes': (work/'bootstrap-runtime087').stat().st_size,
        'runtime_bootstrap_source': source.replace('commercial61-native-087/', 'commercial61-native-101/'),
        'runtime_verified': False, 'reference_platform_preload_delta': '101'}
    for folder in (work, report):
        (folder/'result.json').open('x').write(json.dumps(previous, indent=2))
    print(json.dumps(previous['softbus_reference101'], indent=2))


if __name__ == '__main__':
    main()
