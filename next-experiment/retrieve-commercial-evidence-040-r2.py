from pathlib import Path
import runpy,subprocess
source=runpy.run_path(str(Path(__file__).with_name('retrieve-commercial-evidence-040.py')))['source']
source=source.replace("reports/commercial61-native-040","reports/commercial61-native-040-r2").replace("/home/zoinve/harmony-virgl-883/commercial61-native-040/","/home/zoinve/harmony-virgl-883/commercial61-native-040-r2/")
if __name__=="__main__":exec(compile(source,__file__,"exec"),{"__name__":"__main__","__file__":__file__})
