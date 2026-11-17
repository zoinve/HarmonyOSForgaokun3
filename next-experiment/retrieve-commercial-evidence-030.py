from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('retrieve-commercial-evidence-029.py')))['source'].replace('commercial61-native-029','commercial61-native-030').replace('commercial-return-audit-029','commercial-return-audit-030')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
