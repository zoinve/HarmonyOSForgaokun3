from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('retrieve-commercial-evidence-024.py')))['source'].replace('commercial61-native-024','commercial61-native-025').replace('commercial-return-audit-024','commercial-return-audit-025')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
