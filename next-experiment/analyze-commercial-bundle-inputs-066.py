"""Analyze preserved first-attempt dumps, retaining CRC failures as evidence."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'bundle066', ROOT / 'next-experiment/audit-commercial-bundle-inputs-066.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

if __name__ == '__main__':
    rows = []
    for source in audit.PATHS:
        target = audit.OUT / Path(source).name
        if not target.exists():
            rows.append(dict(original_path=source, extracted=False))
            continue
        row = audit.inspect(target)
        row.update(original_path=source, extracted=True)
        rows.append(row)
    result = dict(original_image_modified=False, operational_boot_performed=False,
                  first_attempt_stopped_on_crc_failure=True,
                  signature_checks_modified=False, files=rows)
    with (audit.OUT / 'result-revision2.json').open('x') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=True)
    for row in rows:
        metadata = row.get('metadata', {})
        print(row['original_path'], 'CRC=', row.get('zip_crc_valid'),
              'bad_member=', row.get('zip_crc_bad_member'),
              'gap=', row.get('pre_central_gap_bytes'),
              'app=', metadata.get('module.json', {}).get('app', {}))
