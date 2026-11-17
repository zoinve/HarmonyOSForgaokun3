"""Observe the existing438 attempt only; expiration never requests a retry."""
from pathlib import Path
import json
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
REPORT = BASE.parent / 'reports/commercial61-native-438'
if __name__ == '__main__':
    assert (REPORT / 'boot-attempt.json').is_file()
    deadline = time.monotonic() + 1100
    while time.monotonic() < deadline:
        result = subprocess.run([sys.executable, str(BASE / 'collect-bluetooth-438-441.py'), 'observe'],
                                capture_output=True, text=True, timeout=25)
        print(result.stdout or result.stderr, flush=True)
        result.check_returncode()
        observation = REPORT / 'boot-observation-441.json'
        if observation.exists() and json.loads(observation.read_text())['returned']:
            break
        time.sleep(30)
    else:
        raise SystemExit('438 observation expired; inspect this attempt, never retry')
