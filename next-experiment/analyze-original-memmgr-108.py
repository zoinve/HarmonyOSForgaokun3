"""Correlate actual directory creation, original SA checks and desktop latency."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'next-experiment'


def sample_blocks(body):
    starts = list(re.finditer(rb'^MEMMGR108_SAMPLE_BEGIN target=(\d+)\n', body, re.M))
    result = []
    for index, match in enumerate(starts):
        block = body[match.start():starts[index + 1].start() if index + 1 < len(starts) else len(body)]
        present = re.findall(rb'^SAMGR_SERVICE id=1909 present=([01])$', block, re.M)
        status = re.findall(rb'^MEMMGR108_SA_PROBE status=(\d+) ', block, re.M)
        complete = re.search(rb'^MEMMGR108_SAMPLE_END target=' + match[1] + rb'$', block, re.M) is not None
        verified = complete and present == [b'1'] and status == [b'0'] and b'SAMGR_SERVICE_PROBE_PASS' in block
        result.append(dict(target=int(match[1]), complete=complete,
            sa_present_values=[int(value) for value in present],
            probe_statuses=[int(value) for value in status], genuine_sa_publication_verified=verified))
    return result


if __name__ == '__main__':
    folder = ROOT / 'reports/commercial61-native-108'
    output = folder / 'memmgr-runtime-analysis.json'
    assert not output.exists()
    manifest = json.loads((folder / 'runtime-evidence/retrieval-manifest.json').read_text())
    hashes = {}
    def read(name):
        data = (folder / 'runtime-evidence/raw' / name).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert digest == manifest['files'][name]['sha256'] and len(data) == manifest['files'][name]['bytes']
        hashes[name] = digest
        return data
    log = read('snapshot075-commercial-memmgr108.log')
    hilog = read('interactive-hilog030.log')
    sanitize = runpy.run_path(str(BASE / 'analyze-original-devicedetect-095.py'))['sanitize']
    paths = []
    for match in re.finditer(rb'^MEMMGR108_PATH_AFTER path=(\S+) created=([01]) uid=(\d+) gid=(\d+) mode=([0-7]+)$', log, re.M):
        paths.append(dict(path=match[1].decode(), created=int(match[2]), uid=int(match[3]), gid=int(match[4]), mode=match[5].decode()))
    samples = sample_blocks(log)
    initial = read('phase-001.log')
    final = read('phase-120.log')
    query_path = folder / 'server-event-analysis.json'
    query = json.loads(query_path.read_text()) if query_path.exists() else None
    events = query['events'] if query else {}
    durations = {}
    for name, start, end in [('client_query', 'client_start', 'client_end'), ('request_to_stage1', 'server_read_request', 'server_stage1')]:
        a, b = events.get(start), events.get(end)
        durations[name] = b['milliseconds'] - a['milliseconds'] if a and b and a['day'] == b['day'] else None
    original_logs = []
    for index, line in enumerate(hilog.splitlines(), 1):
        if len(line) > 1600:
            continue
        if any(token in line for token in (b'/memmgrservice/', b'memmgr no-hyperhold ns:', b'MemMgrService is null', b'GetSaWrap SA:1909 not start')):
            original_logs.append(dict(line=index, text=sanitize(line)))
    runtime = json.loads((folder / 'result.json').read_text())['memmgr108']
    source_paths = [path for path in paths if path['path'].endswith('/memmgr-nohyperhold-v1/memcg')]
    result = dict(run=manifest['run'], verified_input_sha256=hashes,
        preinit_complete=b'MEMMGR108_PREINIT_END service_success_not_inferred=1' in log,
        paths=paths, required_bind_source_created=source_paths[0]['created'] == 1 if len(source_paths) == 1 else None,
        samples=samples, monitor_complete=b'MEMMGR108_OBSERVER_END desktop_not_inferred=1' in log,
        genuine_memory_sa_ever_verified=any(sample['genuine_sa_publication_verified'] for sample in samples),
        genuine_memory_sa_all_samples_verified=(
            b'MEMMGR108_OBSERVER_END desktop_not_inferred=1' in log
            and [sample['target'] for sample in samples] == [20, 40, 60, 80, 100, 120, 140]
            and all(sample['genuine_sa_publication_verified'] for sample in samples)),
        actual_query_durations_ms=durations,
        runtime_path=runtime['runtime_path'], runtime_sha256=runtime['runtime_sha256'],
        original_memory_service_logs=original_logs,
        runtime_helper_execution_marker_observed=b'COMMERCIAL108_MEMORY_PREREQUISITES' in final or b'COMMERCIAL108_MEMORY_PREREQUISITES' in initial,
        changed_original_images=False, completion_state_fabricated=False, desktop_verified=False,
        memory_service_success_is_not_oobe_bypass=True)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: value for k, value in result.items() if k != 'original_memory_service_logs'}, indent=2))
