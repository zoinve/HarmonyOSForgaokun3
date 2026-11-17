"""Verify board audio clock/pinctrl suppliers omitted by snd-only selection."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')


if __name__ == '__main__':
    report = ROOT / 'reports/audio-suppliers-144'
    assert not report.exists()
    host = json.loads((ROOT / 'reports/audio-bluetooth-inputs-134-20261116T023823269998Z/result.json').read_text())
    wanted = ['lpasscc_sc8280xp', 'pinctrl_sc8280xp_lpass_lpi', 'pinctrl_lpass_lpi']
    assert all(name in host['all_module_names'] for name in wanted)
    payload = BUILD / 'commercial61-native-141/initrd.img'
    metadata = json.loads((ROOT / 'reports/commercial61-native-141/result.json').read_text())
    expected = next(r['sha256'] for r in metadata['artifacts'] if r['name'] == 'initrd.img')
    raw = payload.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected
    parser = runpy.run_path(str(ROOT / 'next-experiment/audit-commercial-network-inputs-079.py'))['members']
    members = {n: b for n, _, b in parser(gzip.decompress(raw))}
    modules = {}
    with tempfile.TemporaryDirectory(prefix='suppliers144-') as directory:
        for name in wanted:
            candidates = [(n, b) for n, b in members.items() if n.endswith('.ko') and Path(n).stem.replace('-', '_') == name]
            assert len(candidates) == 1, name
            relative, body = candidates[0]
            local = Path(directory) / Path(relative).name
            local.write_bytes(body)
            fields = {key: subprocess.check_output(['modinfo', '-F', key, str(local)], text=True).strip().splitlines()
                      for key in ['name', 'depends', 'alias', 'firmware', 'vermagic']}
            modules[name] = dict(path=relative, sha256=hashlib.sha256(body).hexdigest(), **fields)
    result = dict(context='Ubuntu enumeration and offline payload, not native driver binding proof',
                  modules=modules, initrd_sha256=expected, target_state_modified=False,
                  native_supplier_binding_verified=False, audio_playback_verified=False)
    report.mkdir()
    (report / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
