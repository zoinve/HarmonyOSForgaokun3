from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('analyze-commercial-minimal-022.py')))['source'].replace('commercial61-native-022','commercial61-native-023').replace('COMMERCIAL022','COMMERCIAL023')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
