"""One actual Wi-Fi reconnect, retaining original services and canonical config."""
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
    work = BUILD / 'commercial61-native-090'
    report = ROOT / 'reports/commercial61-native-090'
    assert not work.exists() and not report.exists()
    previous = json.loads((ROOT / 'reports/commercial61-native-089/result.json').read_text())
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    before = {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD / 'commercial61-native-089/initrd.img').read_bytes()))}
    after = dict(before)
    key = 'native-target/commercial-desktop077.sh'
    after[key] = (before[key][0], (BASE / 'commercial-network-refresh-090.sh').read_bytes())
    assert {n for n in before if before[n] != after[n]} == {key}
    work.mkdir()
    report.mkdir()
    for item in previous['artifacts']:
        if item['name'] == 'initrd.img':
            continue
        source = BUILD / 'commercial61-native-089' / item['name']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item['sha256']
        shutil.copyfile(source, work / item['name'])
    raw = b''.join(pack(n, m, d, i+1) for i, (n, (m, d)) in enumerate(after.items()))
    raw += pack('TRAILER!!!', 0, b'', len(after)+1)
    (work / 'initrd.img').open('xb').write(gzip.compress(raw, compresslevel=6, mtime=0))
    previous['artifacts'] = [dict(name=i['name'], bytes=(work/i['name']).stat().st_size,
        sha256=hashlib.sha256((work/i['name']).read_bytes()).hexdigest()) for i in previous['artifacts']]
    previous.pop('single_stop_diagnostic', None)
    previous['network_refresh_diagnostic'] = dict(changed_members=[key], canonical_config_inherited='088',
        original_wpa_cli=True, maximum_disconnect_requests=1, maximum_reconnect_requests=1,
        no_guide_stop=True, provisioning_modified=False)
    previous['runtime_verified'] = False
    for folder in (work, report):
        (folder / 'result.json').open('x').write(json.dumps(previous, indent=2))
    shutil.copyfile(ROOT / 'reports/commercial61-native-089/config-provenance.json', report / 'config-provenance.json')
    print(json.dumps(previous['network_refresh_diagnostic']))


if __name__ == '__main__':
    main()
