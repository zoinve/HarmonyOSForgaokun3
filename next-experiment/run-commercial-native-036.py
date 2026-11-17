from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-commercial-native-035.py'))) ["source"].replace("commercial61-native-035","commercial61-native-036").replace("commercial-return-audit-035","commercial-return-audit-036").replace("Confirmed pixel readback 035","Reference service startup 036")
source=source.replace("['ssh',", "['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',")
if __name__=="__main__":exec(compile(source,__file__,"exec"),{"__name__":"__main__","__file__":__file__})
