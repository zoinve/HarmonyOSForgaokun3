"""Retain all prior acceptance gates and require actual source-identity verification."""
from pathlib import Path

BASE=Path(__file__).resolve().parent


if __name__=='__main__':
    source=(BASE/'test-live-debug-analysis-161.py').read_text().replace('analyze-live-debug-161.py','analyze-live-debug-164.py')
    for old,new in [('LIVE161_CONTEXT','LIVE164_CONTEXT'),('LIVE161_END','LIVE164_END'),('LIVE161_LOADER','LIVE164_LOADER')]:
        source=source.replace(old,new)
    source=source.replace('LIVE161_STORAGE_READY item=1 readonly=1 source_regular=1',
        'LIVE163_LOG_READY item=1 source_reopened_in_current_mount_namespace=1 original_inode_verified=1\nLIVE163_LOG_READY item=2 source_reopened_in_current_mount_namespace=1 original_inode_verified=1\nLIVE161_STORAGE_READY item=1 readonly=1 source_regular=1',1)
    anchor="        self.assertTrue(summarize(text,client)['authenticated_native_readonly_channel_verified'])"
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+"\n        self.assertFalse(summarize(text.replace('original_inode_verified=1','original_inode_verified=0'),client)['authenticated_native_readonly_channel_verified'])",1)
    exec(compile(source,'test-live-debug-analysis-164.generated.py','exec'),globals())
