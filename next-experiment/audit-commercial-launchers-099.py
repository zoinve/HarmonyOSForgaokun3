"""Inventory the exact launch scripts delivered in 099, without running them."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent


if __name__ == '__main__':
    output = ROOT/'reports/commercial61-native-099/launch-path-audit.json'
    assert not output.exists()
    image = Path('/home/zoinve/harmony-virgl-883/commercial61-native-099/initrd.img')
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    archive = {n: (m, d) for n, m, d in parse(gzip.decompress(image.read_bytes()))}
    selected = {}
    for name in ('native-target/desktop-order020.sh', 'native-target/commercial-direct-desktop-075.sh',
                 'native-target/commercial-desktop077.sh', 'native-target/harmonymac-reference099.sh'):
        mode, body = archive[name]
        selected[name] = dict(mode=oct(mode), sha256=hashlib.sha256(body).hexdigest(),
                              body=body.decode(), scene_start_commands=[line for line in body.decode().splitlines()
                                  if 'aa start -b com.ohos.sceneboard' in line])
    result = dict(scripts=selected, target_booted=False, source_image_written=False,
                  inherited_account_script_contains_scene_start=bool(selected['native-target/desktop-order020.sh']['scene_start_commands']),
                  reference_script_contains_scene_start=bool(selected['native-target/harmonymac-reference099.sh']['scene_start_commands']),
                  runtime_correspondence='099 HiLog aa PIDs 4600 (/usr/bin/aa) and 5059 (/system/bin/aa)',
                  duplicate_launch_causality_for_relaunch_not_proven=True)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(scripts={n: dict(sha256=r['sha256'], scene_start_commands=r['scene_start_commands'])
                                  for n, r in selected.items()},
                         duplicate_launch_causality_for_relaunch_not_proven=True), indent=2))
