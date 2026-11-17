'''Compare source permission IDs to literal candidates without exporting IDs.'''
import hashlib
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
API = runpy.run_path(str(Path(__file__).with_name('audit-settings-state-coherence-188.py')))
LITERALS = ['local', 'LOCAL', 'default', 'DEFAULT', 'localhost', '0', '1', '-1']


def compare_literals(values):
    counts = {literal: sum(value == literal for value in values) for literal in LITERALS}
    other = [value for value in values if value not in LITERALS]
    return dict(known_literal_counts=counts, unclassified_value_count=len(other),
                distinct_unclassified_value_count=len(set(other)), raw_unclassified_values_exported=False)


if __name__ == '__main__':
    folder = ROOT / 'reports/settings-state-deviceids-194'
    assert not folder.exists(), 'immutable result already exists'
    prior_data = (ROOT / 'reports/settings-state-deviceids-193/result.json').read_bytes()
    prior = json.loads(prior_data)
    candidate = json.loads((ROOT / 'reports/settings-data-candidate-191-r2/result.json').read_text())
    image = Path(candidate['candidate_path'])
    assert not subprocess.check_output(['losetup', '-j', str(image)]).strip()
    data = subprocess.run(['debugfs', '-R', 'cat /service/el1/public/access_token/access_token.db', str(image)],
                          capture_output=True, check=True).stdout
    assert hashlib.sha256(data).hexdigest() == prior['original_token_database_sha256']
    connection = API['memory_database'](data)
    try:
        values = [row[0] for row in connection.execute('SELECT device_id FROM permission_state_table')]
        result = compare_literals(values)
    finally:
        connection.close()
    result.update(prior_report_sha256=hashlib.sha256(prior_data).hexdigest(), source_rows=len(values),
                  original_token_database_bytes_unchanged=True, device_identity_rewritten=False,
                  target_modified=False, image_mounted_or_written=False,
                  literal_classification_not_hardware_identity_verification=True,
                  candidate_booted_or_settings_ui_verified=False)
    folder.mkdir()
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
