"""Configuration-only safety checks for the separate official ARM image probe."""
import importlib.util
from pathlib import Path

base = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('official', base / 'official-arm-config.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
root = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921'
rows = [{'name': name, 'path': root + '/original-disks/' + name,
         'bytes': 104857600, 'sha256': 'a' * 64}
        for name in ['system.img', 'vendor.img', 'sys_prod.img', 'userdata.img']]
c = module.build_config(rows, root + '/full-system')
cmd = c['command']
assert cmd[cmd.index('-accel') + 1] == 'kvm'
assert cmd[cmd.index('-display') + 1] == 'none'
boot_args = cmd[cmd.index('-append') + 1].split()
assert 'ohos.boot.hardware=hmos.emulator' in boot_args[:-1], 'hardware parameter must not consume the trailing proc cmdline newline'
assert set(boot_args) == {'console=ttyAMA0', 'rdinit=/init', 'panic=-1', 'loglevel=7', 'ohos.boot.hardware=hmos.emulator'}
for i in range(4):
    serial = ['system', 'vendor', 'sysprod', 'userdata'][i]
    assert cmd.count(f'virtio-blk-pci,drive=d{i},serial=official-{serial},addr=0x{i+3:x}') == 1
assert sum('readonly=on' in part for part in cmd) == 3
assert len(c['disks']) == 4 and not c['disks'][3]['readonly']
assert c['disks'][3]['path'].endswith('/full-system/userdata-permissive.img')
assert c['originals'] == rows
assert 'chipprod' not in str(c) and '-S' in cmd
source = module.make_runner(root + '/full-system', base / 'runner-template.py')
compile(source, 'official-runner', 'exec')
ns = {}
exec(source[:source.index('o=Path(')], ns)
ns['validate_blocks']([{'device': 'd' + str(i), 'inserted': {'ro': i != 3}}
                       for i in range(4)])
try:
    ns['validate_blocks']([{'device': 'd0', 'inserted': {'ro': False}}])
except AssertionError:
    pass
else:
    raise AssertionError('Writable official system disk must be rejected')
print('PASS: official ARM four-disk layout, native KVM and independent userdata guards')
