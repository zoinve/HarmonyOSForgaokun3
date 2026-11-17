"""Separate genuine early kernel readings from missing original-service acceptance."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-131'
    output = report / 'battery-runtime-analysis.json'
    assert not output.exists()
    evidence = report / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, row in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
    name = max((name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log', name)),
               key=lambda name: int(name[6:-4]))
    text = (evidence / 'raw' / name).read_text()
    begin = text.index('GAOKUN_BATTERY131_BEGIN_READ_ONLY')
    end = text.index('GAOKUN_BATTERY131_END_NOT_HDI_ACCEPTANCE', begin)
    section = text[begin:end]
    supplies = {}
    for block in section.split('SUPPLY=')[1:]:
        lines = block.splitlines()
        supplies[lines[0]] = dict(re.findall(r'ATTRIBUTE=([a-z_]+)\n([^\n]+)', '\n'.join(lines[1:])))
    battery = supplies['/sys/class/power_supply/gaokun-ec-battery']
    assert battery['type'] == 'Battery'
    result = dict(run=manifest['run'], verified_files=len(manifest['files']), phase_file=name,
                  phase_sha256=manifest['files'][name]['sha256'], supplies=supplies,
                  battery_module_load_succeeded='PHASE_END huawei_gaokun_battery status=0' in text,
                  real_auxiliary_driver_bound='drivers/huawei_gaokun_battery.psy' in section,
                  genuine_battery_readings_observed=True, temperature_observed='temp' in battery,
                  original_service_started='COMMERCIAL087_TARGET' in text,
                  original_battery_hdi_verified=False, battery_ui_verified=False,
                  seed_load_timed_out='PHASE_END oobe-seed-load123 status=124' in text,
                  loop_setup_refused='NATIVE_ORIGINAL_REFUSED loop_setup' in text,
                  desktop_or_input_regression_inferred=False, new_boot_attempted_by_analysis=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
