"""Export allowlisted profile diagnostics, never raw log message payloads."""
from collections import Counter
from pathlib import Path
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
FUNCTION = re.compile(r'\(([A-Za-z_][A-Za-z_0-9]*):(\d+)\)')
NUMBER = re.compile(r'\b(status|result|ret|error|errno|reason|cause|state|connectState|profileId)\s*[=:]\s*(-?(?:0x[0-9a-fA-F]{1,8}|\d{1,10}))\b', re.I)
SECRET = re.compile(r'passkey|passcode|pin.?code|link.?key|\bpin\b', re.I)
WORDS = ('fail', 'error', 'null', 'invalid', 'denied', 'timeout', 'unsupported',
         'load', 'unload', 'hdf', 'proxy', 'busy', 'connected', 'disconnected',
         'success', 'a2dp', 'hfp', 'sco', 'sdp', 'l2cap', 'codec', 'avdt', 'avrcp')
TOPICS = ('a2dp', 'hfp', 'sco', 'sdp', 'l2cap', 'avdt', 'avrcp', 'acl')


def inspect(stream):
    records = []
    signatures = Counter()
    for index, raw in enumerate(stream, 1):
        line = raw.decode(errors='replace')
        if SECRET.search(line):
            continue
        function = FUNCTION.search(line)
        if not function:
            continue
        name = function[1]
        lower = line.lower()
        if not (any(topic in name.lower() for topic in TOPICS) or
                ('bluetooth' in lower and re.search(r'fail|error|invalid|null', lower))):
            continue
        words = [word for word in WORDS if word in lower]
        fields = [dict(field=key.lower(), value=value) for key, value in NUMBER.findall(line)]
        record = dict(line=index, function=name, diagnostic_words=words, numeric_fields=fields)
        records.append(record)
        signatures[(name, tuple(words), tuple((row['field'], row['value']) for row in fields))] += 1
    return dict(records=records, signatures=[dict(function=key[0], diagnostic_words=list(key[1]),
        numeric_fields=[dict(field=k, value=v) for k, v in key[2]], count=count)
        for key, count in signatures.most_common()], raw_payloads_exported=False,
        addresses_names_keys_passcodes_exported=False, profile_success_inferred=False)


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-458'
    output = report / 'bluetooth-profile-analysis-480.json'
    assert not output.exists()
    reader = runpy.run_path(str(ROOT / 'next-experiment/compress-historical-logs-226.py'))['open_log']
    with reader(report / 'runtime-evidence/raw/interactive-hilog030.log') as stream:
        result = inspect(stream)
    output.open('x').write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(records=len(result['records']), signatures=result['signatures'][:65]), indent=2))
