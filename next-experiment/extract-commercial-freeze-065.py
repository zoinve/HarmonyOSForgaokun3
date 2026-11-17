"""Recover complete original SceneBoard freeze evidence without another boot."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    'fault018', ROOT / 'next-experiment/extract-native-faults-018.py')
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)

if __name__ == '__main__':
    base = ROOT / 'reports/commercial61-native-065'
    source = base / 'runtime-evidence/raw/interactive-faults030.log'
    raw = source.read_bytes()
    rows = parser.extract(raw.decode(errors='strict'))
    selected = [r for r in rows if 'appfreeze-com.ohos.sceneboard' in r['path']]
    assert selected, 'No complete, unchanged SceneBoard freeze report'
    output = base / 'original-freeze-files'
    output.mkdir(exist_ok=False)
    manifest = []
    for row in selected:
        name = 'sample-%02d-%s' % (row['sample'], Path(row['path']).name)
        with (output / name).open('xb') as stream:
            stream.write(row['data'])
        manifest.append(dict(sample=row['sample'], original_path=row['path'],
                             name=name, bytes=len(row['data']),
                             sha256=hashlib.sha256(row['data']).hexdigest()))
    result = dict(source=str(source.relative_to(ROOT)),
                  source_sha256=hashlib.sha256(raw).hexdigest(), files=manifest)
    with (base / 'freeze-extraction.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
