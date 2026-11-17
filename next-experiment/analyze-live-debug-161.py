"""Require the inherited original namespace plus new helper/storage evidence."""
from pathlib import Path
import re
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
parent_summarize = runpy.run_path(str(BASE / 'analyze-live-debug-159.py'))['summarize']


def summarize(text,client):
    normalized = text.replace('LIVE161_CONTEXT','LIVE159_CONTEXT').replace('LIVE161_END','LIVE159_END')
    result = parent_summarize(normalized,client)
    refused = [dict(item=int(item),stage=int(stage),errno=int(error)) for item,stage,error in re.findall(
        r'^LIVE161_STORAGE_REFUSED item=(\d+) stage=(\d+) errno=(\d+)$',text,re.M)]
    ready = [int(item) for item in re.findall(r'^LIVE161_STORAGE_READY item=(\d+) ',text,re.M)]
    loader_ready = len(re.findall(r'^LIVE161_LOADER_READY source_hash_verified=1 ram_hash_verified=1 inherited_log_fds_present=1$',text,re.M)) == 1
    result.update(storage_refusals=refused,storage_ready_items=ready,hash_checked_ram_loader_ready=loader_ready)
    result['authenticated_native_readonly_channel_verified'] = result['authenticated_native_readonly_channel_verified'] and loader_ready and ready==[1,2,3] and not refused
    return result


if __name__ == '__main__':
    source = (BASE / 'analyze-live-debug-157.py').read_text()
    start = source.index('def summarize(')
    end = source.index("\n\nif __name__ == '__main__':",start)
    source = source[:start] + source[end:]
    source = source.replace('commercial61-native-157','commercial61-native-161').replace('live-runtime-analysis-157.json','live-runtime-analysis-161.json')
    source = source.replace("'load_results','contexts',","'load_results','storage_refusals','storage_ready_items','hash_checked_ram_loader_ready','contexts',",1)
    exec(compile(source,'analyze-live-debug-161.generated.py','exec'),{'__name__':'__main__','__file__':__file__,'summarize':summarize})
