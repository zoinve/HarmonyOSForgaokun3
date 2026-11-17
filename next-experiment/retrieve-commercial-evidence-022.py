from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('retrieve-commercial-evidence-016.py')))['source']
source=source.replace('commercial61-native-016-r2','commercial61-native-022').replace('commercial61-native-016-*','commercial61-native-022-*').replace('commercial-return-audit-016','commercial-return-audit-022')
source=source.replace('HostName=10.126.126.14','HostName=192.168.10.128')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
