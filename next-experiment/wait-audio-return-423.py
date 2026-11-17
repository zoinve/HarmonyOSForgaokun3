"""Observe the single420 attempt; never requests or retries a boot."""
from pathlib import Path
import json
import subprocess
import sys
import time

BASE=Path(__file__).resolve().parent
REPORT=BASE.parent/'reports/commercial61-native-420'
if __name__=='__main__':
    assert (REPORT/'boot-attempt.json').is_file()
    deadline=time.monotonic()+1100
    while time.monotonic()<deadline:
        result=subprocess.run([sys.executable,str(BASE/'collect-audio-420-422.py'),'observe'],
                              capture_output=True,text=True,timeout=25)
        print(result.stdout or result.stderr,flush=True)
        result.check_returncode()
        observation=REPORT/'boot-observation-422.json'
        if observation.exists() and json.loads(observation.read_text())['returned']:
            break
        time.sleep(30)
    else:
        raise SystemExit('420 observation expired; inspect existing attempt, never retry')
