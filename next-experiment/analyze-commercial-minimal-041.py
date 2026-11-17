from pathlib import Path
import runpy,subprocess
source=runpy.run_path(str(Path(__file__).with_name('analyze-commercial-minimal-040-r2.py')))['source'].replace("commercial61-native-040-r2","commercial61-native-041").replace("commercial61-native-040","commercial61-native-041").replace("commercial-return-audit-040","commercial-return-audit-041").replace("COMMERCIAL040","COMMERCIAL041").replace("ordered_chain_equals_full_040","ordered_chain_equals_full_041").replace("Reference direct EGL GLES route 040","Original application transaction observation 041")
if __name__=="__main__":exec(compile(source,__file__,"exec"),{"__name__":"__main__","__file__":__file__})
