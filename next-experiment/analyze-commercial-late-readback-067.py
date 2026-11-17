"""Keep actual late GL records separate from desktop/interaction claims."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1] / 'reports/commercial61-native-067'
raw = root / 'runtime-evidence/raw'
manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
for name, item in manifest['files'].items():
    data = (raw / name).read_bytes()
    assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
rows = []
for number, line in enumerate((raw / 'interactive-hilog030.log').read_text(
        errors='replace').splitlines(), 1):
    if not any(marker in line for marker in ['READBACK035 ', 'CONFIG035 ', 'DISPATCH033 ']):
        continue
    match = re.search(r'01-01 (\d+):(\d+):(\d+\.\d+)', line)
    seconds = ((int(match[1])-8)*3600+int(match[2])*60+float(match[3])) if match else None
    values = dict(re.findall(r'(\w+)=([^\s]+)', line))
    rows.append(dict(line=number, guest_seconds=seconds, values=values, text=line))
late = [r for r in rows if r['guest_seconds'] is not None and 100 <= r['guest_seconds'] < 146]
readbacks = [r for r in late if 'READBACK035 ' in r['text']]
result = dict(run=manifest['run'], verified_files=len(manifest['files']),
              all_observation_records=rows, late_observation_records=late,
              late_readback_count=len(readbacks),
              late_confirmed_nine_pixel_reads=sum(r['values'].get('confirmed') == '9' for r in readbacks),
              late_confirmed_nonblack_reads=sum(r['values'].get('confirmed') == '9' and
                  int(r['values'].get('nonblack', '0')) > 0 for r in readbacks),
              sparse_samples_not_full_frame_verification=True,
              desktop_verified=False, interaction_verified=False)
with (root / 'late-readback-analysis.json').open('x') as out:
    json.dump(result, out, indent=2)
print(json.dumps({k: v for k, v in result.items() if k not in (
    'all_observation_records', 'late_observation_records')}, indent=2))
