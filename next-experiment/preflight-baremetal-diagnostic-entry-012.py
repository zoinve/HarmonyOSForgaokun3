"""Fresh baseline after recoverable006 archival."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('preflight-baremetal-diagnostic-entry-011.py')),run_name='offline_generator')['source']
assert source.count('baremetal-boot-entry-preflight-011.json')==1
source=source.replace('baremetal-boot-entry-preflight-011.json','baremetal-boot-entry-preflight-012.json')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
