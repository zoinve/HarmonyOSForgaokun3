from pathlib import Path
import runpy,subprocess
source=runpy.run_path(str(Path(__file__).with_name('run-commercial-native-038.py')))['source'].replace("commercial61-native-038","commercial61-native-039").replace("commercial-return-audit-038","commercial-return-audit-039").replace("COMMERCIAL038","COMMERCIAL039").replace("ordered_chain_equals_full_038","ordered_chain_equals_full_039").replace("Post first-flush capture 038","Post-flush render tasks 039").replace("AUTO RETURN 210 SEC","AUTO RETURN 270 SEC")
if __name__=="__main__":exec(compile(source,__file__,"exec"),{"__name__":"__main__","__file__":__file__})
