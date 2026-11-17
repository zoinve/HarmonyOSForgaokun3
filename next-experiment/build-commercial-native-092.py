"""Add an early RAM-only real-model input; keep both original cores identical."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import shutil

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def main():
    work, report = BUILD/'commercial61-native-092', ROOT/'reports/commercial61-native-092'
    assert not work.exists() and not report.exists()
    work.mkdir()
    report.mkdir()
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE/'build-commercial-native-087.py'))['member']
    before = {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD/'commercial61-native-091/initrd.img').read_bytes()))}
    after = dict(before)
    parameter = 'native-target/graphics016/sys_prod/etc/param/hw_defaults.para'
    sha = lambda body: hashlib.sha256(body).hexdigest()
    wrapper = (BASE/'early-hardware-092.sh').read_text().replace('PARAM_SHA', sha(before[parameter][1])).replace('CORE_SHA', sha(before['init'][1])).encode()
    after['early-hardware092.sh'] = (0o100755, wrapper)
    after['early-sys092'] = (0o040755, b'')
    key = 'native-target/commercial-desktop077.sh'
    anchor = b'/system/bin/id\n'
    assert before[key][1].count(anchor) == 1
    after[key] = (before[key][0], before[key][1].replace(anchor, anchor + b'/system/bin/cat /hardware-early092.log\n', 1))
    previous = json.loads((ROOT/'reports/commercial61-native-091/result.json').read_text())
    for item in previous['artifacts']:
        if item['name'] == 'initrd.img':
            continue
        path = BUILD/'commercial61-native-091'/item['name']
        assert sha(path.read_bytes()) == item['sha256']
        shutil.copyfile(path, work/item['name'])
    raw = b''.join(pack(n, m, d, i+1) for i, (n, (m, d)) in enumerate(after.items()))
    raw += pack('TRAILER!!!', 0, b'', len(after)+1)
    (work/'initrd.img').open('xb').write(gzip.compress(raw, compresslevel=6, mtime=0))
    previous['artifacts'] = [dict(name=i['name'], bytes=(work/i['name']).stat().st_size,
        sha256=sha((work/i['name']).read_bytes())) for i in previous['artifacts']]
    previous['early_real_model_input'] = dict(wrapper_sha256=sha(wrapper),
        original_parameter_sha256=sha(before[parameter][1]), original_core_sha256=sha(before['init'][1]),
        raw_serial_read_by_wrapper=False, physical_firmware_model_only=True,
        original_init_and_bootstrap_unchanged=True, original_parameter_file_in_archive_unchanged=True,
        ram_parameter_model_only=True, existing_091_identity_guards_unchanged=True)
    previous['runtime_verified'] = False
    for folder in (work, report):
        (folder/'result.json').open('x').write(json.dumps(previous, indent=2))
    (report/'early-hardware092.sh').open('xb').write(wrapper)
    shutil.copyfile(ROOT/'reports/commercial61-native-091/config-provenance.json', report/'config-provenance.json')
    print(json.dumps(previous['early_real_model_input'], indent=2))


if __name__ == '__main__':
    main()
