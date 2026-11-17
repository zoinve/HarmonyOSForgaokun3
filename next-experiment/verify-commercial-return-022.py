from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('verify-commercial-return-010.py')))['source'].replace('commercial61-native-010','commercial61-native-022')
source=source.replace('HostName=10.126.126.14','HostName=192.168.10.128')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
