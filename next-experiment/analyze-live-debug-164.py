"""Require both current-namespace same-inode log checks and authenticated live evidence."""
from pathlib import Path
import re
import runpy

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
parent_summarize=runpy.run_path(str(BASE/'analyze-live-debug-161.py'))['summarize']


def summarize(text,client):
    normalized=text.replace('LIVE164_CONTEXT','LIVE161_CONTEXT').replace('LIVE164_END','LIVE161_END').replace('LIVE164_LOADER','LIVE161_LOADER')
    result=parent_summarize(normalized,client)
    ready=[int(item) for item in re.findall(r'^LIVE163_LOG_READY item=(\d+) source_reopened_in_current_mount_namespace=1 original_inode_verified=1$',text,re.M)]
    refused=[dict(item=int(item),stage=int(stage),errno=int(error)) for item,stage,error in re.findall(r'^LIVE163_LOG_REFUSED item=(\d+) stage=(\d+) errno=(\d+)$',text,re.M)]
    result.update(current_namespace_log_ready_items=ready,log_reopen_refusals=refused)
    result['authenticated_native_readonly_channel_verified']=result['authenticated_native_readonly_channel_verified'] and ready==[1,2] and not refused
    return result


if __name__=='__main__':
    source=(BASE/'analyze-live-debug-157.py').read_text()
    start=source.index('def summarize(')
    end=source.index("\n\nif __name__ == '__main__':",start)
    source=source[:start]+source[end:]
    source=source.replace('commercial61-native-157','commercial61-native-164').replace('live-runtime-analysis-157.json','live-runtime-analysis-164.json')
    source=source.replace("'load_results','contexts',","'load_results','storage_refusals','storage_ready_items','current_namespace_log_ready_items','log_reopen_refusals','hash_checked_ram_loader_ready','contexts',",1)
    exec(compile(source,'analyze-live-debug-164.generated.py','exec'),{'__name__':'__main__','__file__':__file__,'summarize':summarize})
