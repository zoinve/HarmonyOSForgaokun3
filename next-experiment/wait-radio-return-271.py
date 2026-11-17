from pathlib import Path
import json
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    deadline = time.monotonic() + 720
    for attempt in range(25):
        proc = subprocess.run([sys.executable, str(BASE / 'collect-radio-266-269.py'), 'observe'],
                              capture_output=True, text=True, timeout=25)
        assert proc.returncode == 0, proc.stderr
        result = json.loads(proc.stdout)
        print(json.dumps(dict(attempt=attempt + 1, observation=result)), flush=True)
        if result.get('returned'):
            break
        if time.monotonic() + 30 >= deadline:
            raise SystemExit('Bounded observation ended; no reboot requested.')
        time.sleep(30)
    else:
        raise SystemExit('Bounded observation ended; no reboot requested.')
