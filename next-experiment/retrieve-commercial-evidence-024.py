from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('retrieve-commercial-evidence-023.py')))['source'].replace('commercial61-native-023','commercial61-native-024').replace('commercial-return-audit-023','commercial-return-audit-024')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
