"""Correlate preserved 099 native/JS dispatch without booting the device."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import tarfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/desktop-dispatch-audit-100'
STAMP = re.compile(rb'^(\d{2}-\d{2}) (\d{2}):(\d{2}):(\d{2})\.(\d{3})\s+(\d+)\s+(\d+)\s')


def parse_line(number, line):
    match = STAMP.match(line)
    if not match:
        return None
    day, hour, minute, second, milli, pid, tid = match.groups()
    return dict(line=number, day=day.decode(),
                milliseconds=((int(hour)*60+int(minute))*60+int(second))*1000+int(milli),
                pid=int(pid), tid=int(tid), body=line)


def elapsed(first, last):
    if first['day'] != last['day']:
        raise ValueError('Do not subtract timestamps across the boot clock change')
    delta = last['milliseconds'] - first['milliseconds']
    if delta < 0:
        raise ValueError('Timestamp order is not monotonic')
    return delta


def select_one(rows, fragment, pid=None, tid=None):
    found = [row for row in rows if fragment in row['body']
             and (pid is None or row['pid'] == pid)
             and (tid is None or row['tid'] == tid)]
    if len(found) != 1:
        raise ValueError(f'Expected one event for {fragment!r}, got {len(found)}')
    return found[0]


def analyze(body):
    rows = [row for number, line in enumerate(body.splitlines(), 1)
            if (row := parse_line(number, line))]
    before = select_one(rows, b'BaseOobeManager: before start oobe end')
    scene = before['pid']
    main = [row for row in rows if row['pid'] == scene and row['tid'] == scene]
    begin = select_one(main, b'device_picker_client.cpp:388]GetTrustedDeviceListWithAbilityFilter# start')
    timeout = select_one(main, b'device_detect_proxy.cpp:270]GetTrustedDeviceListWithAbilityFilter# GetTrustedDeviceListWithAbilityFilterInner timeout')
    leave = select_one(main, b'device_detect_proxy.cpp:272]GetTrustedDeviceListWithAbilityFilter# leave')
    end = select_one(main, b'device_picker_client.cpp:396]GetTrustedDeviceListWithAbilityFilter# end')
    worker = select_one(rows, b'device_detect_proxy.cpp:305]GetTrustedDeviceListWithAbilityFilterInner# GetTrustedDeviceList deviceNum:0', pid=scene)
    native = select_one(rows, b'OnSessionException: bundleName=com.huawei.hmos.hwstartupguide,')
    callback = select_one(main, b'BaseOobeManager: sessionExceptionCallback is called')
    restart = select_one(main, b'BaseOobeManager: start oobe again')
    enabled = select_one(main, b'SCBOobeManager: init ok, provisioned: 0, isOobeEnable: true')
    assert elapsed(before, begin) > 0
    assert elapsed(begin, native) > 0 and elapsed(native, end) > 0
    assert elapsed(end, callback) >= 0
    selected = dict(oobe_enabled=enabled, listener_registration_complete=before,
                    sync_query_begin=begin, nominal_query_timeout=timeout,
                    proxy_leave_log=leave, native_exception=native,
                    worker_reply=worker, sync_query_end=end,
                    js_exception_callback=callback, oobe_restart=restart)
    sanitize = runpy.run_path(str(ROOT/'next-experiment/analyze-original-devicedetect-095.py'))['sanitize']
    def public(row):
        return {**{k: v for k, v in row.items() if k != 'body'}, 'text': sanitize(row['body'])}
    support = [row for row in rows if
               (row['pid'] == 907 and row['tid'] == 6852 and
                any(token in row['body'] for token in
                    (b'localDeviceInfo is nullptr', b'GetTrustedDeviceListWithAbilityFilter', b'CheckDeviceAndReplySync')))
               or b'BusCenterServerDelayInit# try exceeds max times' in row['body']
               or b'LnnGenerateCeParams# gen huks ce key fail' in row['body']]
    gap = [row for row in main if row['day'] == leave['day']
           and leave['milliseconds'] < row['milliseconds'] < end['milliseconds']]
    return dict(scene_pid=scene, events={name: public(row) for name, row in selected.items()},
                durations_ms=dict(sync_query=elapsed(begin, end),
                                  nominal_timeout=elapsed(begin, timeout),
                                  proxy_leave_to_sync_end=elapsed(leave, end),
                                  native_exception_to_js_callback=elapsed(native, callback),
                                  query_end_to_js_callback=elapsed(end, callback),
                                  js_callback_to_restart=elapsed(callback, restart)),
                main_thread_log_rows_inside_gap=len(gap),
                main_thread_absence_is_not_stack_or_scheduler_proof=True,
                supporting_events=[public(row) for row in support],
                inference='The synchronous query interval overlaps delayed JS exception dispatch; '
                          'a blocking native call or wait is strongly indicated, but stacks were not captured.',
                oobe_relaunch_cause_removed=False,
                delay_is_not_evidence_of_a_fixed_relaunch_timer=True,
                duplicate_start_causality_not_established=True,
                softbus_failure_causality_not_established=True)


def main():
    assert not OUT.exists(), 'Preserve numbered evidence'
    source = ROOT/'reports/commercial61-native-099/runtime-evidence'
    manifest_bytes = (source/'retrieval-manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest['physical_serial_guard_passed'] and manifest['original_udid_guard_passed']
    name = 'interactive-hilog030.log'
    with tarfile.open(source/'original.tar') as archive:
        with archive.extractfile('./'+name) as stream:
            body = stream.read()
    digest = hashlib.sha256(body).hexdigest()
    assert digest == manifest['files'][name]['sha256']
    assert len(body) == manifest['files'][name]['bytes']
    result = analyze(body)
    result.update(run=manifest['run'], input_sha256=digest,
                  retrieval_manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
                  original_evidence_modified=False, target_booted=False,
                  original_images_written=False, desktop_verified=False, interaction_verified=False)
    OUT.mkdir()
    with (OUT/'timeline.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({key: result[key] for key in
                      ('scene_pid', 'durations_ms', 'main_thread_log_rows_inside_gap',
                       'target_booted', 'desktop_verified')}, indent=2))


if __name__ == '__main__':
    main()
