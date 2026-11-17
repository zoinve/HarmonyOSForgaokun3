"""Replace the L410 Bluetooth wait chain with a real QCA transport in RAM."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import runpy
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')
IMAGES = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092')


def once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new, 1)


def image_read(image, path):
    return subprocess.check_output(['debugfs', '-R', 'cat ' + path, str(IMAGES / image)], stderr=subprocess.DEVNULL)


def radio_config():
    source = json.loads(image_read('p108-chip_prod.kr990-ext4-v1.img', '/etc/init/hdf_devhost.cfg'))
    hosts = [row for row in source['services'] if row['name'] == 'blue_host']
    assert len(hosts) == 1
    host = hosts[0]
    assert host['uid'] == 'blue_host' and host['path'] == [
        '/vendor/bin/l410_blue_host_fd_launcher', '/vendor/bin/hdf_devhost', '-i', '5', '-n', 'blue_host']
    host['path'] = host['path'][1:]
    for job in source.get('jobs', []):
        job['cmds'] = [cmd for cmd in job.get('cmds', []) if cmd not in
                       ['start l410_hi1103_bt_oam', 'start l410_hi1103_bt_transport']]
    passwd = image_read('p111-system.kr990-ext4-v1.img', '/system/etc/passwd').decode()
    users = [line.split(':') for line in passwd.splitlines() if line.startswith('blue_host:')]
    assert len(users) == 1 and users[0][2] == '3021', 'original service UID must match broker policy'
    return json.dumps(source, indent=2).encode()


def runtime(source):
    anchor = 'static void commercial_graphics016(void)'
    helper = '''static void radio261_bind(void)
{
    const char *sources[] = {"/radio261/hdf_devhost.cfg", "/radio261/libbt_vendor.z.so"};
    const char *targets[] = {"/chip_prod/etc/init/hdf_devhost.cfg", "/vendor/lib64/libbt_vendor.z.so"};
    for (unsigned i = 0; i < 2; ++i) {
        struct stat st;
        if (lstat(targets[i], &st) || !S_ISREG(st.st_mode) ||
            mount(sources[i], targets[i], NULL, MS_BIND, NULL) ||
            mount(NULL, targets[i], NULL, MS_BIND|MS_REMOUNT|MS_RDONLY, NULL))
            fail("QCA radio261 read-only board binding");
    }
    dprintf(1,"RADIO261_ORIGINAL_HDF direct_blue_host=1 original_uid=3021 original_hci_service=1 qca_backend=1 readiness_not_inferred=1\\n");
}

'''
    source = once(source, anchor, helper + anchor)
    return once(source, '    commercial_board004();', '    commercial_board004();\n    radio261_bind();')


def outer(source, old_digest, digest):
    assert source.count('/commercial61-native-253/bootstrap-runtime087') == 5
    source = source.replace('/commercial61-native-253/bootstrap-runtime087', '/commercial61-native-261/bootstrap-runtime087')
    assert source.count(old_digest) == 2
    source = source.replace(old_digest, digest)
    source = once(source, 'static void native_original(void)\n{',
                  'static void native_original(void)\n{\n    pid_t radio261_broker = -1;')
    anchor = '    if(okay){\n        /* Only the temporary diagnostic kernel:'
    start = '''    if (okay) {
        radio261_broker = fork();
        if (!radio261_broker) {
            execl("/radio261/qca-broker", "qca-broker261", "/native-target/native-bt-broker.sock", NULL);
            _exit(90);
        }
        int ready = 0;
        for (unsigned i = 0; i < 50 && radio261_broker > 0; ++i) {
            struct stat node;
            if (!lstat("/native-target/native-bt-broker.sock", &node) &&
                S_ISSOCK(node.st_mode) && node.st_uid == 3021 && (node.st_mode & 0777) == 0600) {
                ready = 1; break;
            }
            usleep(100000);
        }
        if (!ready) {
            dprintf(1,"RADIO261_BROKER unavailable=1 no_hardware_success_claimed=1\\n");
            okay = 0;
        }
    }
'''
    source = once(source, anchor, start + anchor)
    source = once(source, '    persistent172_finish();', '''    if (radio261_broker > 0) {
        kill(radio261_broker, SIGKILL);
        while (waitpid(radio261_broker, NULL, 0) < 0 && errno == EINTR) {}
        dprintf(1,"RADIO261_BROKER stopped=1\\n");
    }
    persistent172_finish();''')
    source = once(source, '    char *args[] = {"/network086-control", pid, (char *)mode, NULL};',
                  '    char *args[] = {!strcmp(mode,"bss-count") ? "/radio261/wifi-count" : "/network086-control", pid, (char *)mode, NULL};')
    source = once(source, '                if(i==7 && started083){',
                  '                if((i==4 || i==10 || i==13) && started083)(void)network083_command(child,"bss-count");\n                if(i==7 && started083){')
    return source


if __name__ == '__main__':
    parent = BUILD / 'commercial61-native-253'
    work = BUILD / 'commercial61-native-261'
    report = ROOT / 'reports/commercial61-native-261'
    assert not work.exists() and not report.exists(), 'preserve numbered evidence'
    config = radio_config()
    metadata = json.loads((ROOT / 'reports/commercial61-native-253/result.json').read_text())
    old_digest = next(row['sha256'] for row in metadata['artifacts'] if row['name'] == 'bootstrap-runtime087')
    sha = lambda data: hashlib.sha256(data).hexdigest()
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    member = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    entries = {n: (m, data) for n, m, data in parser(gzip.decompress((parent / 'minimal-overlay.img').read_bytes()))}
    with tempfile.TemporaryDirectory(prefix='.radio261-', dir=BUILD) as tmp:
        stage = Path(tmp)
        def compile_program(name, source, platform=False, core=False):
            path = stage / (name + '.c')
            path.open('x').write(source)
            compiler = str(BUILD / 'window-bridge/toolchain/ohos-cc') if platform else 'aarch64-linux-gnu-gcc'
            args = [compiler, '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(BASE), '-I', str(parent),
                    '-I', str(ROOT / 'references/L410-HarmonyOS-Adaptations/bluetooth')]
            args += ['-shared', '-fPIC', '-Wl,--no-undefined,-soname,libbt_vendor.z.so'] if platform else ['-static']
            args.append(str(path))
            if core: args.append(str(BASE / 'baremetal-diagnostic-core.c'))
            proc = subprocess.run(args + ['-o', str(stage / name)], capture_output=True, timeout=120)
            assert proc.returncode == 0, proc.stderr.decode(errors='replace')
        compile_program('bootstrap-runtime087', runtime((parent / 'bootstrap-runtime087.c').read_text()))
        digest = sha((stage / 'bootstrap-runtime087').read_bytes())
        compile_program('init', outer((parent / 'init.c').read_text(), old_digest, digest), core=True)
        compile_program('qca-broker', (BASE / 'native-qca-broker-022.c').read_text())
        vendor = (BASE / 'native-qca-vendor-022.c').read_text()
        vendor = once(vendor, '/vendor/lib64/harmony-graphics/native-bt-broker.sock', '/native-bt-broker.sock')
        compile_program('libbt_vendor.z.so', vendor, platform=True)
        count = (BASE / 'network-supplicant-083.c').read_text()
        count = once(count, '{"start", "ping", "scan", "scan_results", "status", "log"}', '{"bss-count"}')
        begin = count.index('static int run_mode(')
        end = count.index('\nint main(', begin)
        count = count[:begin] + '#include "native-wifi-count-261.h"\nstatic int run_mode(const char *mode)\n{\n    (void)mode;\n    return radio261_bss_count();\n}\n' + count[end:]
        compile_program('wifi-count', count)
        mode, wrapper = entries['early-hardware093.sh']
        wrapper = runpy.run_path(str(BASE / 'build-device-profile-258.py'))['profile'](wrapper.decode())
        wrapper = once(wrapper, sha(entries['init'][1]), sha((stage / 'init').read_bytes()))
        entries['early-hardware093.sh'] = (mode, wrapper.encode())
        entries['init'] = (entries['init'][0], (stage / 'init').read_bytes())
        entries['radio261'] = (0o40755, b'')
        entries['radio261/hdf_devhost.cfg'] = (0o100644, config)
        for name in ['qca-broker', 'wifi-count', 'libbt_vendor.z.so']:
            entries['radio261/' + name] = (0o100755, (stage / name).read_bytes())
        raw = b''.join(member(n, mode, data, i+1) for i, (n, (mode, data)) in enumerate(entries.items()))
        overlay = gzip.compress(raw + member('TRAILER!!!', 0, b'', len(entries)+1), compresslevel=6, mtime=0)
        (stage / 'minimal-overlay.img').open('xb').write(overlay)
        (stage / 'early-hardware093.sh').open('x').write(wrapper)
        (stage / 'hdf_devhost.cfg').open('xb').write(config)
        os.link(parent / 'bootstrap', stage / 'bootstrap')
        artifacts = [dict(name=p.name, bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
                     for p in sorted(stage.iterdir()) if p.is_file()]
        stage.rename(work)
    result = dict(parent='253', artifacts=artifacts, runtime_verified=False, installed=False, booted=False,
        bluetooth=dict(original_blue_host_uid=3021, l410_fd_launcher_removed=True,
            hi1103_boot_jobs_removed=True, original_hci_hdi_unchanged=True,
            qca_hci_user_stream=True, transport_namespace='outer initial network namespace',
            commands_or_events_translated=False, initialized_or_paired=False),
        wifi=dict(existing_bridge_unchanged=True, read_only_bss_count_added=True,
            raw_ssid_and_bssid_exported=False, nearby_ui_discovery_verified=False),
        device_info=dict(name='HUAWEI MateBook E Go', model='physical DMI product_name',
            hardware_version='physical DMI product_version', persistent_name_migration_pending=True),
        security_identity_and_serial_logic_unchanged=True, original_images_modified=False,
        active165_modified=False, full_image_clone_created=False, filesystem_validation_suite_rerun=False)
    report.mkdir()
    (report / 'result.json').open('x').write(json.dumps(result, indent=2))
    (report / 'overlay-result.json').open('x').write(json.dumps(dict(bytes=len(overlay), sha256=sha(overlay),
        replaces='set253.img', parent='253', minimal_overlay_only=True), indent=2))
    print(json.dumps({key: value for key, value in result.items() if key != 'artifacts'}, indent=2))
