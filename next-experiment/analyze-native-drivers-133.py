"""Correlate measured sysfs snapshots with unchanged original-service logs."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def summarize(phase, hilog):
    samples = {}
    pattern = re.compile(r'GAOKUN_DRIVER133 stage=(\w+) mono_ms=(\d+) path=(\S+) attr=(\w+) valid=([01]) (?:value=(.*)|errno=(\d+))')
    for line in phase.splitlines():
        match = pattern.fullmatch(line)
        if not match:
            continue
        stage, mono, path, attribute, valid, value, error = match.groups()
        record = samples.setdefault((stage, int(mono), path), {})
        record[attribute] = dict(valid=valid == '1', **({'value': value} if valid == '1' else {'errno': int(error)}))
    def values(attributes):
        return {name: row['value'] for name, row in attributes.items() if row['valid']}
    battery = [values(attrs) for (_, _, path), attrs in samples.items() if path == '/sys/class/power_supply/battery']
    consumer = []
    for number, line in enumerate(hilog.splitlines(), 1):
        if 'powermgr/BatteryInfo:' not in line or 'capacity=' not in line:
            continue
        fields = dict(re.findall(r'([A-Za-z_]+)=([^,\s]+)', line))
        if 'capacity' in fields:
            consumer.append(dict(line=number, fields=fields))
    def matches(row, sample):
        return all(field in row['fields'] and attribute in sample and row['fields'][field] == sample[attribute] for field, attribute in
                   [('capacity', 'capacity'), ('present', 'present'), ('currNow', 'current_now')])
    matched = [row for row in consumer if any(matches(row, sample) for sample in battery
               if sample.get('type') == 'Battery' and sample.get('present') == '1')]
    mock = [dict(line=number, text=line) for number, line in enumerate(hilog.splitlines(), 1)
            if 'power_host/BatteryInfo:' in line and 'create mockFilePath path' in line]
    path_records = [dict(line=number, text=line) for number, line in enumerate(hilog.splitlines(), 1)
                    if 'power_host/BatteryInfo:' in line and 'system battery path is exist' in line]
    requests = [dict(device=int(match[1]), logical_level=int(match[2]))
                for match in re.finditer(r'SetScreenBacklight id:\s*(\d+), level is (\d+)', hilog)]
    backlights = [(stage, mono, values(attrs)) for (stage, mono, path), attrs in samples.items()
                  if path == '/sys/class/backlight/ae96000.dsi.0']
    before = [row for stage, _, row in backlights if stage == 'before_services']
    correlations = []
    for stage, mono, attributes in backlights:
        if stage != 'services_sample' or not all(key in attributes for key in ['brightness', 'max_brightness']):
            continue
        hardware = int(attributes['brightness'])
        maximum = int(attributes['max_brightness'])
        if not 0 < maximum <= 4294967295 or not 0 <= hardware <= maximum:
            continue
        for request in requests:
            if request['device'] != 0 or not 0 <= request['logical_level'] <= 65535:
                continue
            expected = (request['logical_level'] * maximum + 65535 // 2) // 65535
            if hardware == expected:
                correlations.append(dict(mono_ms=mono, logical_level=request['logical_level'],
                                         brightness=hardware, maximum=maximum,
                                         actual_brightness_matches=attributes.get('actual_brightness') == str(hardware),
                                         changed_from_before=any(row.get('brightness') != str(hardware) for row in before)))
    return dict(samples=[dict(stage=stage, mono_ms=mono, path=path, attributes=attrs)
                         for (stage, mono, path), attrs in samples.items()],
                original_battery_consumer_records=consumer, matching_battery_consumer_records=matched,
                original_battery_real_path_records=path_records, original_mock_path_records=mock,
                genuine_battery_consumption_observed=bool(matched and path_records and not mock),
                temperature_measured=any('temp' in row for row in battery),
                health_measured=any('health' in row for row in battery),
                original_optional_defaults_are_not_hardware_measurements=True,
                original_backlight_requests=requests, backlight_readback_correlations=correlations,
                backlight_hardware_readback_correlated=any(row['actual_brightness_matches'] and row['changed_from_before'] for row in correlations),
                physical_luminance_verified=False, brightness_slider_verified=False,
                battery_ui_verified=False, unplug_replug_verified=False, suspend_resume_verified=False,
                seed_verified='OOBE123_SEED_VERIFIED original_images_unchanged=1' in phase,
                seed_load_timed_out='PHASE_END oobe-seed-load123 status=124' in phase)


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-133'
    output = report / 'driver-runtime-analysis.json'
    assert not output.exists()
    evidence = report / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, record in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data) == record['bytes'] and hashlib.sha256(data).hexdigest() == record['sha256']
    phase = max((name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log', name)),
                key=lambda name: int(name[6:-4]))
    hilog = 'interactive-hilog030.log'
    phase_text = (evidence / 'raw' / phase).read_bytes().decode('utf-8', errors='replace')
    hilog_text = (evidence / 'raw' / hilog).read_bytes().decode('utf-8', errors='replace')
    result = summarize(phase_text, hilog_text)
    result.update(run=manifest['run'], verified_files=len(manifest['files']), phase_file=phase,
                  phase_sha256=manifest['files'][phase]['sha256'], hilog_sha256=manifest['files'][hilog]['sha256'],
                  phase_unicode_replacement_characters=phase_text.count(chr(65533)),
                  hilog_unicode_replacement_characters=hilog_text.count(chr(65533)),
                  original_evidence_bytes_unchanged=True)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({name: value for name, value in result.items() if name != 'samples'}, indent=2))
