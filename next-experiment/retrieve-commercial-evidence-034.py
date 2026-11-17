from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('retrieve-commercial-evidence-033.py')))['source'].replace('commercial61-native-033','commercial61-native-034').replace('commercial-return-audit-033','commercial-return-audit-034')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
