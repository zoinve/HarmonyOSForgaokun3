"""Record focused regression results without changing any operational evidence."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

b = Path(__file__).resolve().parent
names = ('test-network-helper-085.py', 'test-network-freeze-085.py', 'test-commercial-probes-085.py',
         'test-network-observer-084.py', 'test-commercial-network-analysis-084.py',
         'test-commercial-native-netmanager-084.py', 'test-commercial-oobe-decoder-079.py')


if __name__ == '__main__':
    records = []
    for name in names:
        path = b / name
        result = subprocess.run([sys.executable, str(path), '-v'], text=True, capture_output=True, timeout=60)
        records.append(dict(name=name, source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
    output = b.parent / 'reports/commercial61-native-085/test-results.json'
    with output.open('x') as stream:
        json.dump(records, stream, indent=2)
    print(json.dumps([dict(name=row['name'], returncode=row['returncode'], summary=row['stderr'].splitlines()[-3:]) for row in records], indent=2))
    raise SystemExit(any(row['returncode'] != 0 for row in records))
