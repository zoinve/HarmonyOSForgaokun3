"""Inspect original UDID module and pinned upstream sources without executing it."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
IMAGE = '/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img'
INIT = 'd6b79e48ac513d1737dd878b53311aa629bc81dc'
SOFTBUS = '5c702fc95bed9442b71e7061e30db21a2c88e598'
DM = '2adef0db2499308206951284bfa49bee675ea0d6'


def main():
    out = ROOT / 'reports/original-udid-inputs-audit-091'
    assert not out.exists()
    repo = ROOT / 'references/OpenHarmony-startup-init-6.0-audit090'
    assert subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip() == INIT
    sources = {}
    for name in ('services/modules/udid/udid_comm.c', 'services/modules/udid/udid_adp.c',
                 'interfaces/innerkits/syspara/parameter.c'):
        body = subprocess.check_output(['git', '-C', str(repo), 'show', INIT + ':' + name])
        sources['startup_init/' + name] = dict(commit=INIT, body=body)
    downloads = [
        ('communication_dsoftbus', SOFTBUS, 'interfaces/kits/common/softbus_error_code.h'),
        ('distributedhardware_device_manager', DM, 'interfaces/inner_kits/native_cpp/src/device_manager_impl.cpp')]
    for repository, commit, path in downloads:
        url = f'https://raw.githubusercontent.com/openharmony/{repository}/{commit}/{path}'
        with urllib.request.urlopen(url, timeout=30) as response:
            body = response.read()
        sources[repository + '/' + path] = dict(commit=commit, url=url, body=body)
    header = sources['communication_dsoftbus/interfaces/kits/common/softbus_error_code.h']['body'].decode()
    part = header.split('SOFTBUS_NETWORK_ERR_BASE = SOFTBUS_ERRNO(LNN_SUB_MODULE_CODE),', 1)[1]
    names = []
    for line in part.splitlines():
        value = line.split('//', 1)[0].strip().rstrip(',')
        if not value:
            continue
        if not re.fullmatch(r'SOFTBUS_[A-Z0-9_]+', value):
            break
        names.append(value)
    base = -((203 << 21) | (4 << 16) | 0xffff)
    mapping = {base + i: name for i, name in enumerate(names, 1)}
    assert mapping[-426049513] == 'SOFTBUS_NETWORK_GET_LOCAL_NODE_INFO_ERR'
    module = subprocess.run(['debugfs', '-R', 'cat /system/lib64/init/libudidmodule.z.so', IMAGE],
                            capture_output=True, check=True).stdout
    assert module.startswith(b'\x7fELF') and len(module) == 8984
    out.mkdir()
    provenance = []
    for index, (name, entry) in enumerate(sources.items()):
        body = entry.pop('body')
        saved = f'{index:02d}-' + Path(name).name
        (out / saved).open('xb').write(body)
        provenance.append(dict(path=name, saved_as=saved, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), **entry))
    path = out/'original-libudidmodule.z.so'
    path.open('xb').write(module)
    symbols = subprocess.check_output(['readelf', '-Ws', str(path)])
    strings = [m.group().decode('ascii') for m in re.finditer(rb'[ -~]{5,}', module)]
    relevant = [s for s in strings if any(k in s.lower() for k in ('udid', 'serial', 'param', 'const.product', 'boot.sn'))]
    (out/'original-module-symbols.txt').open('xb').write(symbols)
    result = dict(upstream_sources=provenance, source_branch='OpenHarmony-6.0-Release',
        public_sources_not_proof_of_private_binary_identity=True,
        original_module=dict(path='/system/lib64/init/libudidmodule.z.so', bytes=len(module),
                             sha256=hashlib.sha256(module).hexdigest(), relevant_strings=relevant),
        mapped_error=dict(value=-426049513, name=mapping[-426049513]),
        original_image_written=False, original_module_executed=False,
        hardware_identity_or_activation_modified=False)
    (out/'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(mapped_error=result['mapped_error'], original_module=result['original_module'],
                         source_count=len(provenance)), indent=2))


if __name__ == '__main__':
    main()
