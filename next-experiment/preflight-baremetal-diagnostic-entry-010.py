"""Fresh baseline after byte-preserving archival of obsolete004 EFI assets."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('preflight-baremetal-diagnostic-entry-009.py')),run_name='offline_generator')['source']
assert source.count('baremetal-boot-entry-preflight-009.json')==1
source=source.replace('baremetal-boot-entry-preflight-009.json','baremetal-boot-entry-preflight-010.json')
if __name__=='__main__':exec(compile(source,'preflight010','exec'),{'__file__':__file__,'__name__':'__main__'})
