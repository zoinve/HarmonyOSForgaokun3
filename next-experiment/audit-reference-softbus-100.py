"""Record the source-image SoftBus preload difference from HarmonyMac."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883/commercial61-native-099')
REF = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816')
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
OUT = ROOT/'reports/desktop-dispatch-audit-100/softbus-reference-comparison.json'
PRELOAD = '/system/lib64/l410-collaboration/libsoftbus_ble_pc_rsp_preload_v1.so'


def main():
    assert not OUT.exists(), 'Preserve numbered evidence'
    revision = subprocess.check_output(['git', '-C', str(REF), 'rev-parse', 'HEAD'], text=True).strip()
    assert revision == 'f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad'
    reference = subprocess.check_output(['git', '-C', str(REF), 'show', 'HEAD:ports/tools/enable-local-services.py'])
    assert (REF/'ports/tools/enable-local-services.py').read_bytes().replace(b'\r\n', b'\n') == reference
    assert PRELOAD.encode() in reference and b"if name=='softbus_server':" in reference
    read = subprocess.run(['/usr/sbin/debugfs', '-R', 'cat /system/etc/init/softbus_server_musl.cfg', str(IMAGE)],
                          capture_output=True, check=True)
    config = json.loads(read.stdout)
    services = [service for service in config['services'] if service['name'] == 'softbus_server']
    assert len(services) == 1
    service = services[0]
    env = [entry for entry in service['env'] if entry.get('name') == 'LD_PRELOAD']
    assert env == [dict(name='LD_PRELOAD', value=PRELOAD)]
    parse = runpy.run_path(str(ROOT/'next-experiment/audit-commercial-network-inputs-079.py'))['members']
    entries = {name: body for name, mode, body in parse(gzip.decompress((BUILD/'initrd.img').read_bytes()))}
    candidates = [name for name in entries if 'softbus' in name.lower()]
    runtime = (BUILD/'bootstrap-runtime087.c').read_bytes()
    result = dict(reference_commit=revision,
                  reference_tool_sha256=hashlib.sha256(reference).hexdigest(),
                  source_config_path='/system/etc/init/softbus_server_musl.cfg',
                  source_config_sha256=hashlib.sha256(read.stdout).hexdigest(),
                  source_service=service,
                  reference_explicitly_removes_platform_preload=True,
                  preload_library=PRELOAD, archive_softbus_named_members=candidates,
                  sealed_archive_sha256=hashlib.sha256((BUILD/'initrd.img').read_bytes()).hexdigest(),
                  runtime_source_sha256=hashlib.sha256(runtime).hexdigest(),
                  runtime_source_mentions_softbus=b'softbus' in runtime.lower(),
                  actual_loaded_library_mapping_not_captured=True,
                  preload_causality_for_ui_stall_or_oobe_relaunch_not_established=True,
                  source_config_read_via_debugfs=True, target_booted=False,
                  image_mounted=False, original_image_written=False,
                  next_boundary='Verify the delivered init chain and library mapping, then consider '
                                'the reference-scoped removal of only this platform BLE preload in RAM. '
                                'Retain stock services, identity, permissions, checks and OOBE recovery.')
    OUT.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({key: result[key] for key in
                      ('source_config_sha256', 'reference_explicitly_removes_platform_preload',
                       'archive_softbus_named_members', 'runtime_source_mentions_softbus', 'target_booted')}, indent=2))


if __name__ == '__main__':
    main()
