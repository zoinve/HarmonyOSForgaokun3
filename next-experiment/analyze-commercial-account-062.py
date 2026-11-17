"""Hash-verified original account/boot lifecycle evidence, not inferred success."""
from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parents[1]
REPORT = BASE / 'reports/commercial61-native-062'


def main():
    destination = REPORT / 'account-analysis-revision2.json'
    assert not destination.exists(), 'Preserve numbered evidence'
    evidence = REPORT / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        blob = (evidence / 'raw' / name).read_bytes()
        assert len(blob) == item['bytes']
        assert hashlib.sha256(blob).hexdigest() == item['sha256']
    log = (evidence / 'raw/interactive-hilog030.log').read_text(errors='replace')
    phases = sorted((evidence / 'raw').glob('phase-*.log'))
    assert phases
    native = phases[-1].read_text(errors='replace').replace('\0', '\n')
    markers = [line for line in native.splitlines() if any(key in line for key in
        ['COMMERCIAL062_ACCOUNT_', 'COMMERCIAL032_SCENEBOARD_',
         'switch the local account', 'failed to switch', 'permission denied'])]
    needles = ['/acm/', 'ActivateOsAccount@', 'ActivateDefaultOsAccount@', 'SendToAMSAccountStart@',
               'OnStartUserDone@', 'SwitchToUser failed:', 'RollBackToEarlierAccount@',
               'scb does not exist', 'read boot completed is true', 'Release RsNode',
               'SystemSetParameter name bootevent.account.ready ',
               'SystemSetParameter name bootevent.boot.completed ',
               'SystemSetParameter name bootevent.bootanimation.',
               'SystemSetParameter name bootevent.wms.ready ']
    timeline = [line for line in log.splitlines() if any(key in line for key in needles)]
    boot_draws = [line for line in log.splitlines() if
        'RSSurfaceRenderNodeDrawable::OnDraw name:BootAnimationNode' in line]
    retry = [line for line in markers if 'COMMERCIAL062_ACCOUNT_RETRY' in line]
    results = [int(m[1]) for m in re.finditer(r'COMMERCIAL062_ACCOUNT_RESULT result=(\d+)', native)]
    successes = [line for line in timeline if 'OnStartUserDone' in line and
        re.search(r'errcode is 0(?:\D|$)', line)]
    account_writes = [line for line in timeline if
        'SystemSetParameter name bootevent.account.ready ' in line and 'ret:0' in line]
    acm_logs = [line for line in timeline if '/acm/' in line]
    denied = [line for line in timeline if 'ActivateOsAccount@' in line and 'permission denied' in line]
    result = dict(run=manifest['run'], verified_files=len(manifest['files']),
        native_markers=markers, original_service_timeline=timeline,
        bootanimation_draw_logs=boot_draws, retry_marker_count=len(retry),
        original_cli_exit_results=results, original_account_success_callbacks=successes,
        original_acm_process_logs=acm_logs, original_activation_permission_denials=denied,
        cli_process_observed=bool(acm_logs), native_marker_absence_not_nonexecution_proof=True,
        original_account_ready_successful_write_logs=account_writes,
        log_write_values_not_recorded=True, missing_logs_not_proof_of_no_execution=True,
        cli_exit_alone_not_activation_proof=True, desktop_verified=False)
    destination.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
