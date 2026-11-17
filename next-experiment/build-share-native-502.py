"""Package real P2P and matching kernel490 modules; preserve desktop drivers."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import runpy
import tarfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')
PRIOR = runpy.run_path(str(BASE / 'build-cpufreq-native-471.py'))


def once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new, 1)


def outer502(source, old_digest, digest):
    source = PRIOR['outer471'](source, old_digest, digest)
    source = source.replace('/commercial61-native-471/bootstrap-runtime087',
                            '/commercial61-native-502/bootstrap-runtime087')
    old = '''            char *icc471[] = {"/bin/busybox", "insmod", "/cpufreq471/icc-osm-l3.ko", NULL};
            (void)probe("cpufreq-icc-provider-471", icc471, 15);
'''
    source = once(source, old,
        '            dprintf(1,"CPUFREQ502_PROVIDER kernel_config_builtin=1 runtime_not_inferred=1\\n");\n')
    source = once(source, '!strcmp(mode, "start") ? 10 : 5',
                  '(!strcmp(mode,"start") || !strcmp(mode,"share-start")) ? 15:5')
    anchor = '                if((i==4 || i==10 || i==13) && started083)'
    source = once(source, anchor, '''                if(i==3 && started083) {
                    int share502 = network083_command(child,"share-start");
                    dprintf(1,"SHARE502_START_RESULT status=%d transfer_verified=0\\n",share502);
                }
                if((i==4 || i==10) && started083)(void)network083_command(child,"share-observe");
''' + anchor)
    return source


def extra502(compile_program, stage, entries):
    PRIOR['extra471'](compile_program, stage, entries)
    assert entries.pop('cpufreq471/icc-osm-l3.ko')[1]
    helper = runpy.run_path(str(BASE / 'share-network-helper-501.py'))['SOURCE']
    compile_program('network086-share502', helper)
    entries['network086-control'] = (0o100755, (stage / 'network086-share502').read_bytes())
    entries['native-target/share501'] = (0o40700, b'')
    result = json.loads((ROOT / 'reports/share-supplicant-499/result.json').read_text())
    binary = Path(result['binary']).read_bytes()
    assert hashlib.sha256(binary).hexdigest() == result['sha256']
    entries['native-target/share501/wpa_supplicant'] = (0o100755, binary)
    entries['native-target/share501/p2p.conf'] = (0o100400, b'''ctrl_interface=DIR=/data/local/tmp/l410_p2p_ctrl GROUP=1010
update_config=0
ap_scan=1
driver_param=use_p2p_netdev=1 use_p2p_group_interface=1
p2p_no_group_iface=0
device_name=HUAWEI MateBook E Go
manufacturer=HUAWEI
model_name=MateBook E Go
model_number=GK-W7X
device_type=1-0050F204-1
config_methods=virtual_push_button physical_display keypad
''')
    tools = json.loads((ROOT / 'reports/share-tools-494/package.json').read_text())
    blob = Path(tools['package']).read_bytes()
    assert hashlib.sha256(blob).hexdigest() == tools['sha256']
    entries['native-target/share494'] = (0o40755, b'')
    with tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz') as archive:
        for item in archive:
            assert not Path(item.name).is_absolute() and '..' not in Path(item.name).parts
            assert item.isdir() or item.isfile()
            entries['native-target/' + item.name] = ((0o40755, b'') if item.isdir() else
                (0o100755, archive.extractfile(item).read()))
    modules = json.loads((ROOT / 'reports/compat-modules-500/result.json').read_text())
    blob = Path(modules['archive']).read_bytes()
    assert hashlib.sha256(blob).hexdigest() == modules['sha256']
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    for name, mode, data in parser(gzip.decompress(blob)):
        entries[name] = (mode, data)


if __name__ == '__main__':
    original = PRIOR
    while 'runtime401' not in original:
        original = original['PRIOR']
    runpy.run_path(str(BASE / 'driver-builder-305.py'))['build'](
        502, original['runtime401'], outer502,
        original['OLD']['AUDIO']['RADIO']['vendor297'], extra502)
