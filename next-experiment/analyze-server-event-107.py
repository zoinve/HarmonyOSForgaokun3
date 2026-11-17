"""Correlate both original DFX snapshots with the actually observed query."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'next-experiment'


def overlaps(day, milliseconds, start, end):
    if milliseconds is None or start is None or end is None:
        return None
    if day != start['day'] or day != end['day']:
        return None
    return start['milliseconds'] <= milliseconds <= end['milliseconds']


if __name__ == '__main__':
    folder = ROOT / 'reports/commercial61-native-107'
    output = folder / 'server-event-analysis.json'
    assert not output.exists()
    manifest = json.loads((folder / 'runtime-evidence/retrieval-manifest.json').read_text())
    hashes = {}
    def read(name):
        data = (folder / 'runtime-evidence/raw' / name).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert digest == manifest['files'][name]['sha256'] and len(data) == manifest['files'][name]['bytes']
        hashes[name] = digest
        return data
    body = read('snapshot075-commercial-server-stack107.log')
    hilog = read('interactive-hilog030.log')
    tools = runpy.run_path(str(BASE / 'audit-desktop-dispatch-100.py'))
    stack_blocks = runpy.run_path(str(BASE / 'analyze-server-stack-104.py'))['stack_blocks']
    query_events = runpy.run_path(str(BASE / 'analyze-server-timing-105.py'))['query_events']
    sanitize = runpy.run_path(str(BASE / 'analyze-original-devicedetect-095.py'))['sanitize']
    trigger = re.findall(rb'^SERVER107_QUERY_EVENT (.*)$', body, re.M)
    starts = list(re.finditer(rb'^SERVER107_DFX_CALL_BEGIN role=(\w+) pid=(\d+) scene_pid=(\d+)\n', body, re.M))
    events, captures = {}, []
    trigger_row = tools['parse_line'](0, trigger[0]) if len(trigger) == 1 else None
    if len(starts) == 2 and trigger_row:
        assert [match[1] for match in starts] == [b'device_manager', b'CollaborationFwk']
        scene = int(starts[0][3])
        assert scene == int(starts[1][3]) == trigger_row['pid'] == trigger_row['tid']
        rows = [row for i, line in enumerate(hilog.splitlines(), 1) if (row := tools['parse_line'](i, line))]
        matches = [row for row in rows if row['body'] == trigger[0]]
        assert len(matches) == 1, 'Trigger not uniquely correlated to preserved original log'
        rows = [row for row in rows if row['day'] == trigger_row['day'] and row['line'] >= matches[0]['line']]
        events = query_events(rows, scene, int(starts[1][2]))
        for index, match in enumerate(starts):
            segment = body[match.start():starts[index + 1].start() if index + 1 < len(starts) else len(body)]
            stamp = re.search(rb'^Timestamp:(\d{4})-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)\.(\d{3})', segment, re.M)
            snapshot_ms, day = None, None
            if stamp:
                year, month, date, h, m, s, ms = map(int, stamp.groups())
                day = f'{month:02d}-{date:02d}'
                snapshot_ms = ((h * 60 + m) * 60 + s) * 1000 + ms
            native = re.findall(rb'APP_STACK_RESULT pid=(\d+) result=(-?\d+) reason=([^\n]*)', segment)
            end = re.search(rb'SERVER107_DFX_CALL_END role=\w+ status=(\d+)', segment)
            blocks = stack_blocks(segment, sanitize)
            captures.append(dict(role=match[1].decode(), pid=int(match[2]),
                timestamp=stamp[0].decode() if stamp else None,
                inside_client_query=overlaps(day, snapshot_ms, events['client_start'], events['client_end']),
                inside_server_request=overlaps(day, snapshot_ms, events['server_read_request'], events['server_reply']),
                native_api_results=[dict(pid=int(pid), result=int(code), reason=sanitize(reason)) for pid, code, reason in native],
                observer_exit_status=int(end[1]) if end else None,
                thread_count=len(blocks), frame_count=sum(len(block['frames']) for block in blocks),
                all_thread_blocks=blocks))
    result = dict(run=manifest['run'], verified_input_sha256=hashes,
        trigger_count=len(trigger), capture_count=len(starts),
        observer_complete=b'SERVER107_END desktop_not_inferred=1' in body,
        observer_refusals=[sanitize(line) for line in body.splitlines() if b'SERVER107_REFUSED' in line],
        events={key: ({**{k: v for k, v in row.items() if k != 'body'}, 'text': sanitize(row['body'])} if row else None) for key, row in events.items()},
        captures=captures, original_state_modified=False, observation_can_perturb_timing=True,
        root_cause_not_inferred_from_trigger=True, desktop_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({**{k: v for k, v in result.items() if k not in ('events', 'captures')},
        'captures': [{k: v for k, v in capture.items() if k != 'all_thread_blocks'} for capture in captures]}, indent=2))
