"""Privacy-limited original volume/AVRCP diagnostics from an existing run."""
from collections import Counter
from pathlib import Path
import json
import re
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
FUNCTION = re.compile(r'\(([A-Za-z_][A-Za-z_0-9]*):(\d+)\)')
FIELDS = re.compile(r'\b(volume|volumeLevel|volLevel|level|keyCode|keyAction|action|operation|opId|status|result|ret|error|errno|reason|direction)\s*[=:]\s*(-?(?:0x[0-9a-fA-F]{1,8}|\d{1,10}))\b', re.I)
SECRET = re.compile(r'passkey|passcode|pin.?code|link.?key|\bpin\b', re.I)


def inspect(stream):
    records = []
    counts = Counter()
    for index, raw in enumerate(stream, 1):
        line = raw.decode(errors='replace')
        if SECRET.search(line):
            continue
        found = FUNCTION.search(line)
        if not found:
            continue
        name = found[1]
        # Do not export ordinary keyboard or text-input records.
        if not re.search(r'volume|volkey|passthrough|pass_through|avrcp', name, re.I):
            continue
        counts[name] += 1
        fields = [dict(field=key.lower(), value=value) for key, value in FIELDS.findall(line)
                  if key.lower() not in ('keycode', 'keyaction')]
        records.append(dict(line=index, function=name, numeric_fields=fields,
            error_word_seen=bool(re.search(r'fail|error|invalid|denied', line, re.I)),
            volume_up_word_seen=bool(re.search(r'volume[_ -]?up', line, re.I)),
            volume_down_word_seen=bool(re.search(r'volume[_ -]?down', line, re.I))))
    return dict(function_counts=dict(counts), records=records,
                physical_or_bluetooth_key_origin_not_inferred=True,
                raw_messages_device_identity_keyboard_text_exported=False,
                volume_down_repaired_or_ui_accepted=False)


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('458', '471')
    report = ROOT / ('reports/commercial61-native-' + sys.argv[1])
    output = report / 'volume-key-analysis-486.json'
    assert not output.exists()
    reader = runpy.run_path(str(ROOT / 'next-experiment/compress-historical-logs-226.py'))['open_log']
    with reader(report / 'runtime-evidence/raw/interactive-hilog030.log') as stream:
        result = inspect(stream)
    output.open('x').write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(function_counts=result['function_counts'],
                         explicit_up_word_records=sum(row['volume_up_word_seen'] for row in result['records']),
                         explicit_down_word_records=sum(row['volume_down_word_seen'] for row in result['records']),
                         error_records=[row for row in result['records'] if row['error_word_seen']][:20]), indent=2))
