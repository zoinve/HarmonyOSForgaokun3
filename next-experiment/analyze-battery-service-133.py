"""Additional service correlation; keep the first conservative analysis intact."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def correlate(analysis, hilog):
    measured = set()
    for sample in analysis['samples']:
        if sample['path'] != '/sys/class/power_supply/battery':
            continue
        values = {name: record['value'] for name, record in sample['attributes'].items() if record['valid']}
        keys = ['capacity', 'present', 'current_now', 'voltage_now']
        if values.get('type') == 'Battery' and values.get('present') == '1' and all(key in values for key in keys):
            measured.add(tuple(values[key] for key in keys))
    matched = []
    for row in analysis['original_battery_consumer_records']:
        keys = ['capacity', 'present', 'currNow', 'voltage']
        fields = row['fields']
        if all(key in fields for key in keys) and tuple(fields[key] for key in keys) in measured:
            matched.append(row)
    root_errors = [dict(line=number, text=line) for number, line in enumerate(hilog.splitlines(), 1)
                   if 'power_host/BatteryInfo:' in line and
                   re.search(r'read path\(/sys/class/power_supply//(?:temp|health|charge_counter|current_avg)\) failed', line)]
    return dict(original_consumer_four_fields_match_real_supply=bool(matched),
                matched_consumer_records=matched,
                original_provider_real_sysfs_root_observed=bool(root_errors),
                original_provider_missing_optional_sysfs_records=root_errors,
                original_mock_path_record_count=len(analysis['original_mock_path_records']),
                genuine_battery_service_data_correlated=bool(matched and root_errors and not analysis['original_mock_path_records']),
                initial_analysis_required_unavailable_uncompressed_success_message=True,
                initial_analysis_preserved=True, battery_ui_verified=False, plug_transition_verified=False,
                temperature_and_health_defaults_not_measurements=True)


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-133'
    output = report / 'battery-service-correlation.json'
    assert not output.exists()
    evidence = report / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    data = (evidence / 'raw/interactive-hilog030.log').read_bytes()
    assert hashlib.sha256(data).hexdigest() == manifest['files']['interactive-hilog030.log']['sha256']
    analysis = json.loads((report / 'driver-runtime-analysis.json').read_text())
    assert analysis['hilog_sha256'] == manifest['files']['interactive-hilog030.log']['sha256']
    module = json.loads((ROOT / 'reports/commercial-battery-module-132/result.json').read_text())
    admission = json.loads((report / 'admission-test.json').read_text())
    assert admission['original_battery_hdi_and_composer_unchanged']
    assert module['only_power_supply_registration_name_changed']
    result = correlate(analysis, data.decode('utf-8', errors='replace'))
    result.update(run=manifest['run'], hilog_sha256=analysis['hilog_sha256'],
                  original_battery_hdi_binary_unchanged=True, actual_ec_access_unchanged=True,
                  battery_module_sha256=module['module_sha256'])
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({key: value for key, value in result.items() if not key.endswith('_records')}, indent=2))
