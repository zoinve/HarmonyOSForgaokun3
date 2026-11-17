from pathlib import Path
import runpy,subprocess
source=runpy.run_path(str(Path(__file__).with_name('run-commercial-native-037.py')))['source'].replace("commercial61-native-037","commercial61-native-038").replace("commercial-return-audit-037","commercial-return-audit-038").replace("COMMERCIAL037","COMMERCIAL038").replace("ordered_chain_equals_full_037","ordered_chain_equals_full_038").replace("Reference namespace corrected startup 037","Post first-flush capture 038")
if __name__=="__main__":exec(compile(source,__file__,"exec"),{"__name__":"__main__","__file__":__file__})
