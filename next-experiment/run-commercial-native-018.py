"""One new 018 attempt; no retries or completed-experiment reruns."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-commercial-native-010.py')))['source']
source=source.replace('commercial61-native-010','commercial61-native-018')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
