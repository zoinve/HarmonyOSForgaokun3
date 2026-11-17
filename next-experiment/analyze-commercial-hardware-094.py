"""Report original identity availability before any late probe action."""
from pathlib import Path
import json
import re
import runpy

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    folder = BASE.parent/'reports/commercial61-native-094'
    raw = folder/'runtime-evidence/raw'
    body = (raw/'snapshot075-commercial-desktop086.log').read_bytes()
    result = runpy.run_path(str(BASE/'analyze-commercial-hardware-091.py'))['analyze'](body)
    text = body.decode('utf-8', errors='replace').replace('\x00', '\n')
    result['early_hardware_records'] = re.findall(r'EARLY093_[^\n]*', text)
    result['early_hardware_statuses'] = [int(n) for n in re.findall(r'EARLY093_RESULT status=(\d+)', text)]
    result['early_sysfs_unmount_statuses'] = [int(n) for n in re.findall(r'EARLY093_UNMOUNT status=(\d+)', text)]
    result['original_identity_valid_before_late_probe'] = any(record['phase'] == 'before' and record['valid_hex64']
        for record in result['original_udid_results'])
    result['privacy_digest_available'] = bool(re.search(r'PRIVACY093_ORIGINAL_UDID_HASH digest=[0-9a-f]{64}', text))
    result['serial_readback_matches_firmware'] = 'HARDWARE091_SERIAL_RECHECK matches_firmware=1' in text
    (folder/'hardware-runtime-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    refresh = runpy.run_path(str(BASE/'analyze-commercial-refresh-090.py'))['analyze']
    result = refresh(body, (raw/'interactive-hilog030.log').read_bytes())
    (folder/'network-refresh-runtime-analysis.json').open('x').write(json.dumps(result, indent=2))
