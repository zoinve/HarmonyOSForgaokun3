"""Real processes and captured pixels, never installation-only desktop acceptance."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('analyze-commercial-minimal-019.py')))['source']
source=source.replace('commercial61-native-019','commercial61-native-020').replace('COMMERCIAL019','COMMERCIAL020')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
