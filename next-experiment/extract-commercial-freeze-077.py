"""Recover intact copies without accepting corrupted interleaved snapshots."""
from pathlib import Path
import hashlib
import json
import runpy

b = Path(__file__).resolve().parent
root = b.parent / 'reports/commercial61-native-077'

if __name__ == '__main__':
    manifest = json.loads((root / 'runtime-evidence/retrieval-manifest.json').read_text())
    name = 'interactive-faults030.log'
    body = (root / 'runtime-evidence/raw' / name).read_bytes()
    assert len(body) == manifest['files'][name]['bytes']
    assert hashlib.sha256(body).hexdigest() == manifest['files'][name]['sha256']
    rows, rejected = runpy.run_path(str(b / 'native-fault-snapshots-078.py'))['extract'](body)
    selected = [r for r in rows if 'appfreeze-com.ohos.sceneboard-' in r['path']]
    assert selected, 'No complete original SceneBoard report'
    out = root / 'original-freeze-files'
    out.mkdir(exist_ok=False)
    files, hashes = [], set()
    for row in selected:
        digest = hashlib.sha256(row['data']).hexdigest()
        if digest in hashes:
            continue
        hashes.add(digest)
        name = 'sample-%02d-%s' % (row['sample'], Path(row['path']).name)
        (out / name).open('xb').write(row['data'])
        files.append(dict(sample=row['sample'], original_path=row['path'], name=name,
                          bytes=len(row['data']), sha256=digest))
    result = dict(source_sha256=hashlib.sha256(body).hexdigest(), files=files,
                  complete_sceneboard_copies=len(selected), rejected_snapshots=rejected,
                  missing_bytes_never_repaired=True)
    (root / 'freeze-extraction.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
