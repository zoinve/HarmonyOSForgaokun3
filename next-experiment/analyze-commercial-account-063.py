"""Correlate bounded script-file snapshots with original account lifecycle logs."""
from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parents[1]
REPORT = BASE / 'reports/commercial61-native-063'


def main():
    destination = REPORT / 'account-analysis.json'
    assert not destination.exists(), 'Preserve numbered evidence'
    evidence = REPORT / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        blob = (evidence / 'raw' / name).read_bytes()
        assert len(blob) == item['bytes']
        assert hashlib.sha256(blob).hexdigest() == item['sha256']
    log = (evidence / 'raw/interactive-hilog030.log').read_text(errors='replace')
    phases = sorted((evidence / 'raw').glob('phase-*.log'))
    native = phases[-1].read_text(errors='replace')
    pattern = (r'COMMERCIAL063_OUTER_STREAM_BEGIN path=(\S*/commercial-account-order063\.log) limit=(\d+)\n'
               r'(.*?)\nCOMMERCIAL063_OUTER_STREAM_END path=\1 bytes=(\d+) eof=(\d+) errno=(\d+)')
    snapshots = []
    for match in re.finditer(pattern, native, re.S):
        snapshots.append(dict(path=match[1], limit=int(match[2]), text=match[3],
            bytes=int(match[4]), eof=int(match[5]), errno=int(match[6]),
            utf8_byte_count_matches=len(match[3].encode()) == int(match[4])))
    valid = [item for item in snapshots if item['errno'] == 0 and item['eof'] == 1
             and item['utf8_byte_count_matches']]
    selected = max(valid, key=lambda item: item['bytes']) if valid else None
    script = selected['text'] if selected else ''
    if selected:
        (REPORT / 'account-script063.log').open('x').write(script)
    needles = ['ActivateDefaultOsAccount@', 'SendToAMSAccountStart@', 'OnStartUserDone@',
        'ActivateOsAccount@', 'SwitchToUser failed:', 'RollBackToEarlierAccount@',
        'scb does not exist', 'read boot completed is true', 'Release RsNode',
        'SystemSetParameter name bootevent.account.ready ',
        'SystemSetParameter name bootevent.boot.completed ',
        'SystemSetParameter name bootevent.bootanimation.',
        'SystemSetParameter name bootevent.wms.ready ']
    timeline = [line for line in log.splitlines() if any(key in line for key in needles)]
    starts = [line for line in log.splitlines() if '/accountmgr/' in line and
              '[OnStart@account_mgr_service.cpp:' in line and 'start is triggered' in line]
    callbacks = [line for line in timeline if 'OnStartUserDone' in line and
                 re.search(r'errcode is 0(?:\D|$)', line)]
    draws = [line for line in log.splitlines() if
             'RSSurfaceRenderNodeDrawable::OnDraw name:BootAnimationNode' in line]
    result = dict(run=manifest['run'], verified_files=len(manifest['files']),
        snapshot_metadata=[{k: v for k, v in item.items() if k != 'text'} for item in snapshots],
        selected_script_log=selected, original_service_timeline=timeline,
        original_account_service_start_logs=starts, original_account_success_callbacks=callbacks,
        script_retry_marker_count=script.count('COMMERCIAL063_ACCOUNT_SERVICE_RETRY'),
        original_init_stop_results=re.findall(r'COMMERCIAL063_ACCOUNT_STOP_RESULT result=(\d+)', script),
        original_init_start_results=re.findall(r'COMMERCIAL063_ACCOUNT_START_RESULT result=(\d+)', script),
        script_observed_account_ready_values=re.findall(r'COMMERCIAL063_ACCOUNT_READY observed_value=(\S+)', script),
        bootanimation_draw_logs=draws, log_write_values_not_recorded=True,
        restart_exit_alone_not_activation_proof=True, missing_logs_not_nonexecution_proof=True,
        desktop_verified=False)
    destination.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
