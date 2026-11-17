"""Reuse overlapping-hex digest audit, retaining private config084 on-device."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'audit-wifi-evidence-secrecy-084-r2.py'))['source']
source = source.replace('reports/commercial61-native-084/', 'reports/commercial61-native-085/')
source = source.replace('evidence-secrecy-audit-revision2.json', 'evidence-secrecy-audit.json')

if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
