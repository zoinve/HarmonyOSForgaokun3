"""Reuse hash-checked desktop observation and authenticated-channel analysis."""
from pathlib import Path
import json
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-173'

if __name__ == '__main__':
    summarize = runpy.run_path(str(BASE / 'analyze-persistent-desktop-168.py'))['summarize']
    result = dict(previous_persistent_boot=summarize(ROOT / 'reports/commercial61-native-168'),
        current_persistent_boot=summarize(REPORT))
    (REPORT / 'persistent-desktop-analysis.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    source = (BASE / 'analyze-live-debug-164.py').read_text().replace('commercial61-native-164','commercial61-native-173')
    source = source.replace('live-runtime-analysis-164.json','live-runtime-analysis-173.json')
    exec(compile(source,'analyze-live-debug-173.generated.py','exec'),
        {'__name__':'__main__','__file__':__file__})
