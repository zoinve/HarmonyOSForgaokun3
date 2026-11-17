"""Locate persisted trace-control boundaries, without asserting a panic cause."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1] / 'reports/commercial61-native-048'


def controls(text):
    result = []
    for match in re.finditer(r'^COMMERCIAL048_TRACE_CONTROL_(BEGIN|END) ([^\n]+)', text, re.MULTILINE):
        row = dict(stage=match[1], text=match[2])
        path = re.search(r'path=([^\s]+)', match[2])
        assert path
        row['path'] = path[1]
        result.append(row)
    return result


def main():
    recovered = (ROOT / 'recovered-evidence/recovery-manifest.json').exists()
    evidence = ROOT / ('recovered-evidence' if recovered else 'runtime-evidence')
    manifest = json.loads((evidence / ('recovery-manifest.json' if recovered else 'retrieval-manifest.json')).read_text())
    for name, item in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
    phases = sorted(name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log', name))
    assert phases
    text = (evidence / 'raw' / phases[-1]).read_text(errors='replace')
    rows = controls(text)
    begins = [row for row in rows if row['stage'] == 'BEGIN']
    ends = [row for row in rows if row['stage'] == 'END']
    result = dict(run=manifest['run'], recovered_evidence=recovered, verified_files=len(manifest['files']),
                  source_phase=phases[-1], controls=rows,
                  last_started=begins[-1] if begins else None,
                  last_completed=ends[-1] if ends else None,
                  final_boundary_unclosed=bool(rows and rows[-1]['stage'] == 'BEGIN'),
                  trace_ready=re.findall(r'COMMERCIAL048_TRACE_READY[^\n]+', text),
                  trace_failures=re.findall(r'COMMERCIAL048_TRACE_SETUP_FAILED[^\n]+', text),
                  original_samples=re.findall(r'NATIVE_ORIGINAL_SAMPLE[^\n]+', text),
                  normal_target_timeout='COMMERCIAL048 target_timeout=1' in text,
                  target_exit=re.findall(r'COMMERCIAL048_TARGET_EXIT[^\n]+', text),
                  persisted_boundary_is_not_failure_cause_proof=True, actual_desktop_verified=False)
    (ROOT / 'boundary-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'controls'}, indent=2))


if __name__ == '__main__':
    main()
