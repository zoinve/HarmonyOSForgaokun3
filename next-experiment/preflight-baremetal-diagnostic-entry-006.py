"""Fresh post-cleanup baseline for independently staged 009 assets."""
from pathlib import Path

source=Path(__file__).with_name('preflight-baremetal-diagnostic-entry-005.py').read_text()
assert source.count('baremetal-boot-entry-preflight-005.json')==1
source=source.replace('baremetal-boot-entry-preflight-005.json','baremetal-boot-entry-preflight-006.json')
if __name__=='__main__':exec(compile(source,'preflight006','exec'),{'__file__':__file__,'__name__':'__main__'})
