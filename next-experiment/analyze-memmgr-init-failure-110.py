"""Correlate preserved, already decoded original 109 initialization failures."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'next-experiment'
TOKENS = [b'WriteToFile_ failed. 300 > /dev/memcg/memory.app_score',
          b'WriteToFile_ failed. Root > /dev/memcg/memory.name',
          b'ReadScoreAndReclaimRatiosFromKernel_ file not found. /dev/memcg/memory.zswapd_single_memcg_param',
          b'Init init failed', b'Init ReclaimStrategyManager init failed', b'OnStart init failed']


if __name__ == '__main__':
    folder = ROOT / 'reports/commercial61-native-109'
    output = ROOT / 'reports/memmgr-init-failure-analysis-110.json'
    assert not output.exists()
    manifest = json.loads((folder / 'runtime-evidence/retrieval-manifest.json').read_text())
    log = (folder / 'runtime-evidence/raw/interactive-hilog030.log').read_bytes()
    digest = hashlib.sha256(log).hexdigest()
    assert digest == manifest['files']['interactive-hilog030.log']['sha256']
    sanitize = runpy.run_path(str(BASE / 'analyze-original-devicedetect-095.py'))['sanitize']
    pattern = re.compile(rb'^(\d\d-\d\d) (\d\d):(\d\d):(\d\d)\.(\d{3})\s+(\d+)\s+(\d+) [A-Z] C02699/memmgrservice/MM: (.*)$')
    events = []
    for index, line in enumerate(log.splitlines(), 1):
        match = pattern.match(line)
        if not match or match[8] not in TOKENS:
            continue
        events.append(dict(line=index, day=match[1].decode(), pid=int(match[6]), tid=int(match[7]),
            milliseconds=((int(match[2]) * 60 + int(match[3])) * 60 + int(match[4])) * 1000 + int(match[5]),
            token_index=TOKENS.index(match[8]), text=sanitize(line)))
    assert [event['token_index'] for event in events] == list(range(len(TOKENS)))
    assert len({(event['pid'], event['tid'], event['day'], event['milliseconds']) for event in events}) == 1
    memory = json.loads((folder / 'memmgr-runtime-analysis.json').read_text())
    stacks = json.loads((folder / 'memory-stack-analysis.json').read_text())
    assert all(capture['pid'] == events[-1]['pid'] for capture in stacks['captures'])
    assert not memory['genuine_memory_sa_ever_verified']
    stamp = re.fullmatch(r'Timestamp:1970-(\d\d-\d\d) (\d\d):(\d\d):(\d\d)\.(\d{3})', stacks['captures'][0]['timestamp_lines'][0])
    assert stamp and stamp[1] == events[-1]['day']
    first_ms = ((int(stamp[2]) * 60 + int(stamp[3])) * 60 + int(stamp[4])) * 1000 + int(stamp[5])
    result = dict(run=manifest['run'], raw_hilog_sha256=digest, events=events,
        already_decoded_original_messages=True, new_dictionary_generation_or_boot_required=False,
        original_init_failure_explicitly_observed=True,
        failing_component='ReclaimStrategyManager::Init',
        original_missing_interfaces=['/dev/memcg/memory.app_score', '/dev/memcg/memory.name',
            '/dev/memcg/memory.zswapd_single_memcg_param'],
        original_onstart_skips_publish_after_init_failure=True,
        publish_failure_not_the_observed_startup_branch=True,
        earlier_claim_that109_logs_cannot_distinguish_init_from_publish_corrected=True,
        first_dfx_snapshot_after_failure_ms=first_ms - events[-1]['milliseconds'],
        exact_low_level_return_and_errno_not_captured=True,
        original_empty_ext4_bind_observed_in109=True,
        root_field56_is_allocated_reclaim_ratios_not_kernel_file=True,
        desktop_verified=False, next_fix_requires_real_kernel_interface_not_fake_files=True)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
