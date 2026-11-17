"""Read exact payload topology and module metadata without target operations."""
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
    report = ROOT / 'reports/audio-topology-140'
    assert not report.exists()
    path = BUILD / 'commercial61-native-136/initrd.img'
    metadata = json.loads((ROOT / 'reports/commercial61-native-136/result.json').read_text())
    expected = next(row['sha256'] for row in metadata['artifacts'] if row['name'] == 'initrd.img')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected
    parser = runpy.run_path(str(ROOT / 'next-experiment/audit-commercial-network-inputs-079.py'))['members']
    entries = {name: body for name, _, body in parser(gzip.decompress(raw))}
    topology = [dict(path=n, bytes=len(b), sha256=hashlib.sha256(b).hexdigest())
                for n, b in entries.items() if 'firmware/' in n and ('tplg' in n.lower() or 'topology' in n.lower())]
    module_paths = {Path(n).stem.replace('-', '_'): (n, b) for n, b in entries.items() if n.endswith('.ko')}
    host = json.loads((ROOT / 'reports/audio-bluetooth-inputs-134-20261116T023823269998Z/result.json').read_text())
    modules = {}
    with tempfile.TemporaryDirectory(prefix='topology140-') as directory:
        for row in host['selected_modules']:
            name = row['name']
            if name not in module_paths:
                modules[name] = dict(packaged=False)
                continue
            relative, body = module_paths[name]
            local = Path(directory) / Path(relative).name
            local.write_bytes(body)
            fields = {key: subprocess.check_output(['modinfo', '-F', key, str(local)], text=True).strip().splitlines()
                      for key in ['depends', 'alias', 'firmware']}
            modules[name] = dict(packaged=True, path=relative, sha256=hashlib.sha256(body).hexdigest(), **fields)
    source = BUILD / 'native-binder-kernel-045/linux/sound/soc/qcom/qdsp6/topology.c'
    text = source.read_text()
    assert 'qcom/%s/%s-tplg.bin' in text and 'card->driver_name' in text and 'card->name' in text
    result = dict(context='offline exact payload inspection, not native playback acceptance',
                  initrd_sha256=expected, topology_files=topology, modules=modules,
                  kernel_topology_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  firmware_name_template='qcom/<card driver_name>/<card name>-tplg.bin',
                  target_state_modified=False, audio_playback_verified=False)
    report.mkdir()
    (report / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(topology_files=topology, unpackaged_host_modules=[n for n, r in modules.items() if not r['packaged']]), indent=2))
