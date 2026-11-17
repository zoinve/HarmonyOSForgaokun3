"""Read original memory-service DFX and namespace evidence with hash checks."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'next-experiment'


if __name__ == '__main__':
    folder = ROOT / 'reports/commercial61-native-109'
    output = folder / 'memory-stack-analysis.json'
    assert not output.exists()
    manifest = json.loads((folder / 'runtime-evidence/retrieval-manifest.json').read_text())
    name = 'snapshot075-commercial-memmgr-stack109.log'
    body = (folder / 'runtime-evidence/raw' / name).read_bytes()
    digest = hashlib.sha256(body).hexdigest()
    assert digest == manifest['files'][name]['sha256'] and len(body) == manifest['files'][name]['bytes']
    sanitize = runpy.run_path(str(BASE / 'analyze-original-devicedetect-095.py'))['sanitize']
    stack_blocks = runpy.run_path(str(BASE / 'analyze-server-stack-104.py'))['stack_blocks']
    starts = list(re.finditer(rb'^MEMSTACK109_DFX_BEGIN phase=(first|later) pid=(\d+)\n', body, re.M))
    captures = []
    for index, match in enumerate(starts):
        segment = body[match.start():starts[index + 1].start() if index + 1 < len(starts) else len(body)]
        phase, pid = match[1], int(match[2])
        native = re.findall(rb'^APP_STACK_RESULT pid=(\d+) result=(-?\d+) reason=([^\n]*)$', segment, re.M)
        end = re.findall(rb'^MEMSTACK109_DFX_END phase=' + phase + rb' status=(\d+) success_not_inferred=1$', segment, re.M)
        blocks = stack_blocks(segment, sanitize)
        namespace = re.search(rb'^MEMSTACK109_NAMESPACE_BEGIN phase=' + phase + rb'\n(.*?)^MEMSTACK109_NAMESPACE_END phase=' + phase + rb'$', segment, re.M | re.S)
        captures.append(dict(phase=phase.decode(), pid=pid,
            native_api_results=[dict(pid=int(p), result=int(code), reason=sanitize(reason)) for p, code, reason in native],
            exit_statuses=[int(status) for status in end],
            genuine_native_stack_verified=(len(native) == 1 and int(native[0][0]) == pid
                and int(native[0][1]) == 0 and end == [b'0'] and bool(blocks)),
            thread_count=len(blocks), frame_count=sum(len(block['frames']) for block in blocks),
            timestamp_lines=[sanitize(line) for line in segment.splitlines() if line.startswith(b'Timestamp:')],
            all_thread_blocks=blocks,
            namespace_complete=namespace is not None,
            namespace_lines=[sanitize(line) for line in namespace[1].splitlines()] if namespace else []))
    result = dict(run=manifest['run'], input_sha256=digest, captures=captures,
        observer_complete=re.search(rb'^MEMSTACK109_END desktop_not_inferred=1$', body, re.M) is not None,
        refusals=[sanitize(line) for line in body.splitlines() if line.startswith(b'MEMSTACK109_REFUSED')],
        both_original_stacks_verified=([capture['phase'] for capture in captures] == ['first', 'later']
            and all(capture['genuine_native_stack_verified'] for capture in captures)),
        initialization_overlap_not_assumed=True, observation_can_perturb_timing=True,
        service_publication_not_inferred=True, desktop_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({**{k: v for k, v in result.items() if k != 'captures'},
        'captures': [{k: v for k, v in capture.items() if k not in ('all_thread_blocks', 'namespace_lines')} for capture in captures]}, indent=2))
