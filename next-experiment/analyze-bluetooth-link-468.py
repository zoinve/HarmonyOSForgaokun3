"""Index original Bluetooth link/profile functions and numeric results only."""
from collections import Counter, deque
from pathlib import Path
import json
import re
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
FUNCTION = re.compile(r'\(([A-Za-z_][A-Za-z_0-9]*):(\d+)\)')
NUMBER = re.compile(r'\b(status|result|ret|error|errno|reason|cause)\s*[=:]\s*(-?(?:0x[0-9a-fA-F]{1,8}|\d{1,10}))\b', re.I)
SECRET = re.compile(r'passkey|passcode|pin.?code|link.?key|\bpin\b', re.I)
TOPICS = ('pair', 'bond', 'connect', 'auth', 'encrypt', 'l2cap', 'sdp', 'a2dp', 'hfp', 'hid', 'profile')


def inspect(stream):
    counts = Counter()
    recent = deque(maxlen=160)
    for index, raw in enumerate(stream, 1):
        line = raw.decode(errors='replace')
        if 'bluetooth_service' not in line:
            continue
        found = FUNCTION.search(line)
        if not found or not any(topic in found[1].lower() for topic in TOPICS):
            continue
        name = found[1]
        counts[name] += 1
        numbers = [] if SECRET.search(line) else [dict(field=key.lower(), value=value)
            for key, value in NUMBER.findall(line)]
        recent.append(dict(line=index, function=name, numeric_fields=numbers,
                           error_word_seen=bool(re.search(r'fail|error', line, re.I))))
    return dict(function_counts=dict(sorted(counts.items())), last_link_profile_records=list(recent),
                raw_device_names_addresses_keys_exported=False, numeric_fields_not_success_inferred=True,
                original_service_pairing_or_profile_acceptance_inferred=False)


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['438', '458']
    report = ROOT / ('reports/commercial61-native-' + sys.argv[1])
    output = report / 'bluetooth-link-index-468.json'
    assert not output.exists()
    manifest = json.loads((report / 'runtime-evidence/retrieval-manifest.json').read_text())
    assert 'interactive-hilog030.log' in manifest['files']
    reader = runpy.run_path(str(ROOT / 'next-experiment/compress-historical-logs-226.py'))['open_log']
    with reader(report / 'runtime-evidence/raw/interactive-hilog030.log') as stream:
        result = inspect(stream)
    result['run'] = manifest['run']
    output.open('x').write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(run=result['run'], function_counts=result['function_counts'],
                         indexed_recent_records=len(result['last_link_profile_records'])), indent=2))
