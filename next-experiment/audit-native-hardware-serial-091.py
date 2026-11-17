"""Read real firmware serial sources on Ubuntu; export metadata, never values."""
from pathlib import Path
import json
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent.parent
SSH = 'C:/Windows/System32/OpenSSH/ssh.exe'
REMOTE = r'''
from pathlib import Path
import hashlib, json, re
paths = [
 '/sys/class/dmi/id/product_serial', '/sys/class/dmi/id/board_serial',
 '/sys/class/dmi/id/chassis_serial', '/sys/firmware/devicetree/base/serial-number',
 '/sys/devices/soc0/serial_number', '/sys/devices/system/soc/soc0/serial_number',
 '/sys/class/dmi/id/sys_vendor', '/sys/class/dmi/id/product_name']
rows = []
placeholders = {b'none', b'unknown', b'defaultstring', b'tobefilledbyo.e.m.', b'notspecified', b'systemserialnumber'}
for name in paths:
    path = Path(name)
    try:
        data = path.read_bytes()
        value = data.rstrip(b'\x00\r\n ')
        normalized = value.lower().replace(b' ', b'')
        plausible = bool(re.fullmatch(rb'[A-Za-z0-9_.:/-]{6,64}', value))
        plausible = plausible and normalized not in placeholders and len(set(normalized)) > 1
        rows.append(dict(path=name, resolved=str(path.resolve()), readable=True,
            raw_bytes=len(data), value_bytes=len(value), sha256=hashlib.sha256(value).hexdigest(),
            nonplaceholder_printable_candidate=plausible,
            is_serial_source='serial' in name, value_exported=False))
    except OSError as error:
        rows.append(dict(path=name, readable=False, errno=error.errno, value_exported=False))
print(json.dumps(dict(ubuntu_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
    sources=rows, only_metadata_exported=True, hardware_or_parameter_values_changed=False)))
'''


if __name__ == '__main__':
    folder = ROOT/'reports/native-hardware-serial-audit-091'
    assert not folder.exists()
    command = [SSH, '-i', 'C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
        '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
        '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
        '-o', 'ConnectTimeout=10', 'matebook', 'sudo -n python3 -c ' + shlex.quote(REMOTE)]
    response = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
    result = json.loads(response.stdout)
    assert result['only_metadata_exported'] and not result['hardware_or_parameter_values_changed']
    folder.mkdir()
    (folder/'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
