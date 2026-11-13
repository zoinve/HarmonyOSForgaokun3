"""Fresh post-cleanup baseline for allocator diagnostic013."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('preflight-baremetal-diagnostic-entry-008.py')),run_name='offline_generator')['source']
assert source.count('baremetal-boot-entry-preflight-008.json')==1
source=source.replace('baremetal-boot-entry-preflight-008.json','baremetal-boot-entry-preflight-009.json')
if __name__=='__main__':exec(compile(source,'preflight009','exec'),{'__file__':__file__,'__name__':'__main__'})
