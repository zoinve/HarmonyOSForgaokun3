"""Correlate original DFX time with the initial client and server query only."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'next-experiment'


def first_event(rows, fragment, pid, tid=None, after=-1, before=24*60*60*1000,
                line_after=-1, line_before=2**63):
    found = [r for r in rows if fragment in r['body'] and r['pid'] == pid
             and (tid is None or r['tid'] == tid) and after <= r['milliseconds'] <= before
             and line_after < r['line'] < line_before]
    return min(found, key=lambda r: (r['milliseconds'], r['line'])) if found else None


def query_events(rows, scene, server):
    start_mark = b'device_picker_client.cpp:388]GetTrustedDeviceListWithAbilityFilter# start'
    end_mark = b'device_picker_client.cpp:396]GetTrustedDeviceListWithAbilityFilter# end'
    request_mark = b'ReadAbilityFilterList# abilityFilterList length:3'
    start = first_event(rows, start_mark, scene, scene)
    assert start, 'Initial captured SceneBoard query start missing'
    next_start = first_event(rows, start_mark, scene, scene, start['milliseconds'], line_after=start['line'])
    client_limit = next_start['line'] if next_start else 2**63
    end = first_event(rows, end_mark, scene, scene, start['milliseconds'],
                      line_after=start['line'], line_before=client_limit)
    upper = end['milliseconds'] if end else start['milliseconds']+60000
    request = first_event(rows, request_mark, server, after=start['milliseconds'], before=upper,
                          line_after=start['line'], line_before=client_limit)
    assert request, 'Initial query server request missing'
    next_request = first_event(rows, request_mark, server, request['tid'], request['milliseconds'],
                               line_after=request['line'])
    server_limit = min(client_limit, next_request['line'] if next_request else 2**63)
    stage = first_event(rows, b'GetTrustedDeviceListWithAbilityFilter# event = SERVICE_COLLABORATION_EVENT; stage = 1; res = 1; err = 0',
                        server, request['tid'], request['milliseconds'], upper,
                        line_after=request['line'], line_before=server_limit)
    reply = first_event(rows, b'CheckDeviceAndReplySync# CheckDeviceAndReplySync deviceNum:0',
                        server, request['tid'], request['milliseconds'], upper,
                        line_after=request['line'], line_before=server_limit)
    return dict(client_start=start, server_read_request=request,
                server_stage1=stage, server_reply=reply, client_end=end)


if __name__ == '__main__':
    folder = ROOT/'reports/commercial61-native-105'
    output = folder/'server-capture-timing.json'
    assert not output.exists()
    manifest = json.loads((folder/'runtime-evidence/retrieval-manifest.json').read_text())
    def read(name):
        body = (folder/'runtime-evidence/raw'/name).read_bytes()
        assert hashlib.sha256(body).hexdigest() == manifest['files'][name]['sha256']
        assert len(body) == manifest['files'][name]['bytes']
        return body
    capture = read('snapshot075-commercial-server-stack105.log')
    hilog = read('interactive-hilog030.log')
    tools = runpy.run_path(str(BASE/'audit-desktop-dispatch-100.py'))
    sanitize = runpy.run_path(str(BASE/'analyze-original-devicedetect-095.py'))['sanitize']
    rows = [row for i, line in enumerate(hilog.splitlines(), 1) if (row := tools['parse_line'](i, line))]
    marker = re.search(rb'SERVER105_CAPTURE_BEGIN server_pid=(\d+) scene_pids=(\d+) ', capture)
    assert marker
    server, scene = map(int, marker.groups())
    stamp = re.search(rb'^Timestamp:(\d{4})-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)\.(\d{3})', capture, re.M)
    assert stamp, 'No original DFX timestamp; overlap cannot be proved'
    year, month, day, hour, minute, second, milli = map(int, stamp.groups())
    day_text = f'{month:02d}-{day:02d}'
    rows = [r for r in rows if r['day'] == day_text]
    snapshot_ms = ((hour*60+minute)*60+second)*1000+milli
    events = query_events(rows, scene, server)
    start, end = events['client_start'], events['client_end']
    request, stage, reply = events['server_read_request'], events['server_stage1'], events['server_reply']
    durations = {}
    for name, a, b in [('client_query', start, end), ('server_request_to_stage1', request, stage), ('server_stage1_to_reply', stage, reply)]:
        durations[name] = tools['elapsed'](a, b) if a and b else None
    relevant = json.loads((folder/'server-stack-analysis.json').read_text())
    thread_headers = [block['header'] for block in relevant['relevant_thread_blocks']]
    before_uptime = re.search(rb'SERVER105_CAPTURE_BEGIN[^\n]*\n(\d+\.\d+) ', capture)
    after_uptime = re.search(rb'SERVER105_CAPTURE_END[^\n]*\n(\d+\.\d+) ', capture)
    assert before_uptime and after_uptime
    order = [capture.find(token) for token in (b'SERVER105_DFX_CALL_BEGIN', b'APP_STACK_RESULT', b'SERVER105_CAPTURE_END', b'SERVER105_TASK_SURVEY_BEGIN')]
    result = dict(run=manifest['run'], server_pid=server, server_request_tid=request['tid'], scene_pid=scene,
        events={key: ({**{k: v for k, v in row.items() if k != 'body'}, 'text': sanitize(row['body'])} if row else None) for key, row in events.items()},
        durations_ms=durations, dfx_snapshot_timestamp=stamp[0].decode(),
        snapshot_after_client_return_ms=snapshot_ms-end['milliseconds'] if end else None,
        snapshot_inside_client_query=(start['milliseconds'] <= snapshot_ms <= end['milliseconds']) if end else None,
        snapshot_inside_server_request=(request['milliseconds'] <= snapshot_ms <= reply['milliseconds']) if reply else None,
        dfx_call_uptime_begin=float(before_uptime[1]), dfx_call_uptime_end=float(after_uptime[1]),
        dfx_call_before_proc_survey=all(p >= 0 for p in order) and order == sorted(order),
        request_thread_in_relevant_stacks=any(re.match(r'Tid:\s*'+str(request['tid'])+r'\b', header) for header in thread_headers),
        first_query_wait_root_cause_proven=False,
        proc_samples_are_post_capture_only=True, original_evidence_modified=False,
        desktop_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'events'}, indent=2))
