"""Order438 shutdown records without exporting raw application log data."""
from pathlib import Path
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-438'
    output = report / 'exit-analysis-449.json'
    assert not output.exists()
    phase = json.loads((report / 'audio-analysis-446.json').read_text())['phase_file']
    reader = runpy.run_path(str(ROOT / 'next-experiment/compress-historical-logs-226.py'))['open_log']
    prefixes = ('COMMERCIAL087 target_timeout=', 'COMMERCIAL087_TARGET_EXIT ',
                'AUDIO316_TRANSPORT', 'AUDIO411_SHUTDOWN ', 'AUDIO321_BROKER ',
                'BT435_SESSION ', 'PERSISTENT172_FINISH', 'NATIVE_DIAGNOSTIC_END',
                'COMMERCIAL087_STOPPED ', 'COMMERCIAL087 fallback_reboot=')
    rows = []
    with reader(report / 'runtime-evidence/raw' / phase) as stream:
        for line, raw in enumerate(stream, 1):
            text = raw.decode(errors='replace').strip()
            if text.startswith(prefixes):
                rows.append(dict(line=line, record=text))
    result = dict(phase_file=phase, records=rows, reboot_cause_not_inferred=True)
    output.open('x').write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
