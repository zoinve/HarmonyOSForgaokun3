"""Establish whether the native DFX snapshot overlaps the original query."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'next-experiment'


if __name__ == '__main__':
    folder = ROOT/'reports/commercial61-native-104'
    output = folder/'server-capture-timing.json'
    assert not output.exists()
    manifest = json.loads((folder/'runtime-evidence/retrieval-manifest.json').read_text())
    def read(name):
        body = (folder/'runtime-evidence/raw'/name).read_bytes()
        assert hashlib.sha256(body).hexdigest() == manifest['files'][name]['sha256']
        assert len(body) == manifest['files'][name]['bytes']
        return body
    capture = read('snapshot075-commercial-server-stack104.log')
    hilog = read('interactive-hilog030.log')
    tools = runpy.run_path(str(BASE/'audit-desktop-dispatch-100.py'))
    sanitize = runpy.run_path(str(BASE/'analyze-original-devicedetect-095.py'))['sanitize']
    rows = [row for i, line in enumerate(hilog.splitlines(), 1) if (row := tools['parse_line'](i, line))]
    marker = re.search(rb'SERVER104_CAPTURE_BEGIN server_pid=(\d+) scene_pids=(\d+) ', capture)
    assert marker
    server, scene = map(int, marker.groups())
    one = tools['select_one']
    start = one(rows, b'device_picker_client.cpp:388]GetTrustedDeviceListWithAbilityFilter# start', pid=scene, tid=scene)
    end = one(rows, b'device_picker_client.cpp:396]GetTrustedDeviceListWithAbilityFilter# end', pid=scene, tid=scene)
    request = one(rows, b'ReadAbilityFilterList# abilityFilterList length:3', pid=server)
    stage = one(rows, b'GetTrustedDeviceListWithAbilityFilter# event = SERVICE_COLLABORATION_EVENT; stage = 1; res = 1; err = 0', pid=server, tid=request['tid'])
    reply = one(rows, b'CheckDeviceAndReplySync# CheckDeviceAndReplySync deviceNum:0', pid=server, tid=request['tid'])
    stamp = re.search(rb'^Timestamp:(\d{4})-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)\.(\d{3})', capture, re.M)
    assert stamp
    year, month, day, hour, minute, second, milli = map(int, stamp.groups())
    assert year == 2026 and start['day'] == end['day'] == f'{month:02d}-{day:02d}'
    snapshot_ms = ((hour*60+minute)*60+second)*1000+milli
    events = dict(client_start=start, server_read_request=request, server_stage1=stage, server_reply=reply, client_end=end)
    native = one(rows, b'OnSessionException: bundleName=com.huawei.hmos.hwstartupguide,')
    callback = one(rows, b'BaseOobeManager: sessionExceptionCallback is called', pid=scene, tid=scene)
    restart = one(rows, b'BaseOobeManager: start oobe again', pid=scene, tid=scene)
    events.update(native_guide_exception=native, js_exception_callback=callback, oobe_restart=restart)
    result = dict(run=manifest['run'], server_pid=server, server_request_tid=request['tid'], scene_pid=scene,
        events={key: {**{k: v for k, v in row.items() if k != 'body'}, 'text': sanitize(row['body'])} for key, row in events.items()},
        durations_ms=dict(client_query=tools['elapsed'](start, end),
            server_request_to_stage1=tools['elapsed'](request, stage),
            server_stage1_to_reply=tools['elapsed'](stage, reply),
            native_exception_to_js=tools['elapsed'](native, callback)),
        dfx_snapshot_timestamp=stamp[0].decode(),
        snapshot_after_client_return_ms=snapshot_ms-end['milliseconds'],
        snapshot_inside_client_query=start['milliseconds'] <= snapshot_ms <= end['milliseconds'],
        snapshot_inside_server_request=request['milliseconds'] <= snapshot_ms <= reply['milliseconds'],
        first_query_wait_cause_proven_by_this_snapshot=False,
        observer_pre_capture_task_survey_is_avoidable_work=True,
        exact_time_spent_in_task_survey_not_recorded=True,
        original_evidence_modified=False, desktop_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'events'}, indent=2))
