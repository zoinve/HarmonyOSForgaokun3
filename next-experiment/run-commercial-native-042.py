from pathlib import Path
import runpy,subprocess
source=runpy.run_path(str(Path(__file__).with_name('run-commercial-native-041.py')))['source'].replace("commercial61-native-041","commercial61-native-042").replace("commercial-return-audit-041","commercial-return-audit-042").replace("COMMERCIAL041","COMMERCIAL042").replace("ordered_chain_equals_full_041","ordered_chain_equals_full_042").replace("libcommercial_rs_observer041.so","libcommercial_rs_observer042.so").replace("Original application transaction observation 041","Original transaction mode and state 042")
if __name__=="__main__":exec(compile(source,__file__,"exec"),{"__name__":"__main__","__file__":__file__})
