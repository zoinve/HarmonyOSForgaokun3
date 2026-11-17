"""Original identity API evidence plus the real early model-input outcome."""
from pathlib import Path
import json
import re
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent


if __name__ == '__main__':
    folder = ROOT/'reports/commercial61-native-092'
    raw = folder/'runtime-evidence/raw'
    body = (raw/'snapshot075-commercial-desktop086.log').read_bytes()
    result = runpy.run_path(str(BASE/'analyze-commercial-hardware-091.py'))['analyze'](body)
    text = body.decode('utf-8', errors='replace').replace('\x00', '\n')
    result['early_model_records'] = re.findall(r'EARLY092_[^\n]*', text)
    result['early_model_statuses'] = [int(n) for n in re.findall(r'EARLY092_RESULT status=(\d+)', text)]
    result['early_sysfs_unmount_statuses'] = [int(n) for n in re.findall(r'EARLY092_UNMOUNT status=(\d+)', text)]
    (folder/'hardware-runtime-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    refresh = runpy.run_path(str(BASE/'analyze-commercial-refresh-090.py'))['analyze']
    result = refresh(body, (raw/'interactive-hilog030.log').read_bytes())
    (folder/'network-refresh-runtime-analysis.json').open('x').write(json.dumps(result, indent=2))
