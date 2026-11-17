from pathlib import Path
import runpy,subprocess
source=runpy.run_path(str(Path(__file__).with_name('retrieve-commercial-evidence-036.py')))['source'].replace("commercial61-native-036","commercial61-native-037").replace("commercial-return-audit-036","commercial-return-audit-037").replace("COMMERCIAL036","COMMERCIAL037").replace("ordered_chain_equals_full_036","ordered_chain_equals_full_037").replace("Reference service startup 036","Reference namespace corrected startup 037")
if __name__=="__main__":exec(compile(source,__file__,"exec"),{"__name__":"__main__","__file__":__file__})
