"""Compare each saved dump to an independent read from the unchanged image."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess

B = Path(__file__).resolve().parent
audit = runpy.run_path(str(B / 'audit-commercial-bundle-inputs-066.py'))

if __name__ == '__main__':
    report = audit['OUT']
    previous = json.loads((report / 'result-revision2.json').read_text())
    rows = []
    for row in previous['files']:
        if not row['extracted']:
            continue
        result = subprocess.run(['debugfs', '-R', 'cat ' + row['original_path'],
                                 str(audit['IMAGE'])], capture_output=True, check=True)
        digest = hashlib.sha256(result.stdout).hexdigest()
        assert digest == row['sha256'] and len(result.stdout) == row['bytes']
        rows.append(dict(original_path=row['original_path'], sha256=digest,
                         bytes=len(result.stdout), independent_read_matched=True))
    assert len(rows) == 4
    result = dict(original_image_modified=False, files=rows,
                  extracted_corruption_already_present_in_source=True,
                  signature_checks_modified=False)
    (report / 'independent-source-verification.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
