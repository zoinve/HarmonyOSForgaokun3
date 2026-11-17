'''Parse original vector-valued device IDs without exposing opaque values.'''
import hashlib
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
API = runpy.run_path(str(Path(__file__).with_name('audit-settings-state-coherence-188.py')))


def decode_counts(values):
    counts = dict(json_empty_array=0, json_zero_array=0, json_empty_string_array=0,
                  json_other_array=0, json_zero_scalar=0, json_other_value=0,
                  non_json=0)
    for value in values:
        try:
            decoded = json.loads(value)
        except (ValueError, TypeError):
            counts['non_json'] += 1
            continue
        if isinstance(decoded, list):
            if not decoded:
                kind = 'json_empty_array'
            elif all((type(item) is int and item == 0) or item == '0' for item in decoded):
                kind = 'json_zero_array'
            elif all(item == '' for item in decoded):
                kind = 'json_empty_string_array'
            else:
                kind = 'json_other_array'
        elif (type(decoded) is int and decoded == 0) or decoded == '0':
            kind = 'json_zero_scalar'
        else:
            kind = 'json_other_value'
        counts[kind] += 1
    return counts


if __name__ == '__main__':
    folder = ROOT / 'reports/settings-state-deviceids-195'
    assert not folder.exists(), 'immutable result already exists'
    prior_data = (ROOT / 'reports/settings-state-deviceids-194/result.json').read_bytes()
    earlier = json.loads((ROOT / 'reports/settings-state-deviceids-193/result.json').read_text())
    candidate = json.loads((ROOT / 'reports/settings-data-candidate-191-r2/result.json').read_text())
    image = Path(candidate['candidate_path'])
    assert not subprocess.check_output(['losetup', '-j', str(image)]).strip()
    data = subprocess.run(['debugfs', '-R', 'cat /service/el1/public/access_token/access_token.db', str(image)],
                          capture_output=True, check=True).stdout
    assert hashlib.sha256(data).hexdigest() == earlier['original_token_database_sha256']
    connection = API['memory_database'](data)
    try:
        values = [row[0] for row in connection.execute('SELECT device_id FROM permission_state_table')]
        counts = decode_counts(values)
    finally:
        connection.close()
    unknown = sum(counts[key] for key in ['json_other_array', 'json_other_value', 'non_json'])
    result = dict(prior_report_sha256=hashlib.sha256(prior_data).hexdigest(), source_rows=len(values),
                  decoded_counts=counts, opaque_or_nonzero_decoded_rows=unknown,
                  original_token_database_bytes_unchanged=True, device_identity_rewritten=False,
                  raw_device_ids_or_tokens_exported=False, image_mounted_or_written=False,
                  target_modified=False, classification_not_hardware_identity_verification=True,
                  candidate_booted_or_settings_ui_verified=False)
    folder.mkdir()
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
