"""Read existing preserved logs; do not boot or change the target."""
from pathlib import Path
import collections
import hashlib
import json
import re
import tarfile

ROOT = Path(__file__).resolve().parent.parent
archive = ROOT / 'reports/commercial61-native-092/runtime-evidence/original.tar'
out = ROOT / 'reports/original-devicedetect-095.json'
pattern = re.compile(rb'collabfwk|devicedetect|device.?detect|cfwk|devicepicker|CollaborationFwk', re.I)


def sanitize(line):
    line = re.sub(rb'(?<![A-Za-z0-9])[A-Za-z0-9]{16}(?![A-Za-z0-9])', b'[IDENTIFIER16_REDACTED]', line)
    line = re.sub(rb'(?<![0-9a-fA-F])[0-9a-fA-F]{32,}(?![0-9a-fA-F])', b'[HEX_REDACTED]', line)
    line = re.sub(rb'(?i)((?:udid|serial|token|password|sn)\s*[:=]\s*)[^\s,;]+', rb'\1[PRIVATE_REDACTED]', line)
    return line.decode('utf-8', errors='replace').replace('\x00', '').rstrip()


if __name__ == '__main__':
    assert not out.exists()
    counts = collections.Counter()
    selected = []
    seen = set()
    names = ('./phase-120.log', './snapshot075-commercial-desktop086.log', './interactive-hilog030.log')
    with tarfile.open(archive) as tar:
        for name in names:
            with tar.extractfile(name) as stream:
                for line in stream:
                    if len(line) > 16384 or not pattern.search(line):
                        continue
                    counts[name] += 1
                    text = sanitize(line)
                    if text not in seen:
                        seen.add(text)
                        selected.append(dict(file=name, line=text))
    with archive.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    result = dict(source=str(archive.relative_to(ROOT)), source_sha256=digest,
                  matching_lines=dict(counts), unique_lines=len(selected),
                  lines=selected, original_evidence_modified=False,
                  target_booted=False, service_failure_not_inferred_from_wait_alone=True)
    out.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({key: value for key, value in result.items() if key != 'lines'}, indent=2))
