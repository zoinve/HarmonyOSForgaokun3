from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('retrieve-commercial-evidence-034.py')))['source'].replace('commercial61-native-034','commercial61-native-035').replace('commercial-return-audit-034','commercial-return-audit-035')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
