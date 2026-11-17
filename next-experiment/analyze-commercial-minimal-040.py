from pathlib import Path
import runpy,subprocess
source=runpy.run_path(str(Path(__file__).with_name('analyze-commercial-minimal-039.py')))['source'].replace("commercial61-native-039","commercial61-native-040").replace("commercial-return-audit-039","commercial-return-audit-040").replace("COMMERCIAL039","COMMERCIAL040").replace("ordered_chain_equals_full_039","ordered_chain_equals_full_040").replace("Post-flush render tasks 039","Reference direct EGL GLES route 040")
if __name__=="__main__":exec(compile(source,__file__,"exec"),{"__name__":"__main__","__file__":__file__})
