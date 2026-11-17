from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('verify-commercial-return-033.py')))['source'].replace('commercial61-native-033','commercial61-native-034')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
