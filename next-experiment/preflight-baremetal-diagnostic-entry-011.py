"""Fresh baseline after byte-preserving obsolete005 asset archival."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('preflight-baremetal-diagnostic-entry-010.py')),run_name='offline_generator')['source']
assert source.count('baremetal-boot-entry-preflight-010.json')==1
source=source.replace('baremetal-boot-entry-preflight-010.json','baremetal-boot-entry-preflight-011.json')
if __name__=='__main__':exec(compile(source,'preflight011','exec'),{'__file__':__file__,'__name__':'__main__'})
