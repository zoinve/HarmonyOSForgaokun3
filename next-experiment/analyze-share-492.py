"""Export only function identifiers and counts from original sharing logs."""
from collections import Counter
from pathlib import Path
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
FUNCTION = re.compile(r'\(([A-Za-z_][A-Za-z_0-9]*):(\d+)\)')
CATEGORY = re.compile(r'p2p|softbus|huawei.?share|hwshare|magiclink', re.I)
SECRET = re.compile(r'password|passphrase|psk|passkey|credential|link.?key', re.I)


def inspect(stream):
    counts = Counter()
    failures = Counter()
    for raw in stream:
        line = raw.decode(errors='replace')
        if not CATEGORY.search(line) or SECRET.search(line):
            continue
        found = FUNCTION.search(line)
        if not found:
            continue
        name = found[1]
        counts[name] += 1
        if re.search(r'\bfail(?:ed|ure)?\b|\berror\b|unsupported|not ready|not exist', line, re.I):
            failures[name] += 1
    return dict(function_counts=dict(counts.most_common()),
                failure_word_counts=dict(failures.most_common()),
                raw_messages_or_peer_identifiers_exported=False,
                failure_word_is_not_causal_proof=True,
                huawei_share_transfer_verified=False)


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-471'
    output = report / 'share-analysis-492.json'
    assert not output.exists(), 'preserve numbered evidence'
    reader = runpy.run_path(str(ROOT / 'next-experiment/compress-historical-logs-226.py'))['open_log']
    with reader(report / 'runtime-evidence/raw/interactive-hilog030.log') as stream:
        result = inspect(stream)
    output.open('x').write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
