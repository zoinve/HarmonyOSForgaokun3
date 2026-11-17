"""Compare preserved logs only; never launch, mount, or modify a target."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = {
    'account_service_start': '/accountmgr/AccountMgrService: [OnStart@account_mgr_service.cpp:521]',
    'default_account_activation': 'Start to activate default account',
    'account100_storage_unlock': 'OS account:100 is unlocked.',
    'account100_ams_start': 'Start OS account 100',
    'account100_start_callback_error22': 'OnStartUserDone id is 100, errcode is 22.',
    'foreground_account_query_error': 'GetForegroundOsAccountLocalId failed',
    'settings_start': 'StartAbility com.huawei.hmos.settings/com.huawei.hmos.settings.MainAbility',
    'first_unlock_refusal': 'no startup before device first unlock',
    'screen_unlock_2097253': 'DoProcess err: ScreenUnlock_2097253',
    'user0_default_locked': 'userId=0, default screenLocked: true',
    'system_accounts_config_parse_error': 'Failed to parse systemAccounts',
}


def inspect(path):
    data = path.read_bytes()
    lines = data.decode('utf-8', errors='replace').splitlines()
    events = {}
    for name, pattern in PATTERNS.items():
        matches = [i for i, line in enumerate(lines, 1) if pattern in line]
        events[name] = dict(count=len(matches), first_line=matches[0] if matches else None,
                            last_line=matches[-1] if matches else None)
    return dict(path=path.relative_to(ROOT).as_posix(),
                sha256=hashlib.sha256(data).hexdigest(), events=events)


def main():
    output = ROOT / 'reports/settings-account-204'
    if output.exists():
        raise SystemExit('Refusing to overwrite numbered evidence')
    runs = {number: inspect(ROOT / f'reports/commercial61-native-{number}/runtime-evidence/raw/interactive-hilog030.log')
            for number in ('173', '201')}
    fault = ROOT / 'reports/commercial61-native-201/runtime-evidence/raw/interactive-faults030.log'
    fault_data = fault.read_bytes()
    fault_lines = fault_data.decode('utf-8', errors='replace').splitlines()
    stop = [i for i, line in enumerate(fault_lines, 1) if 'stop service accountmgr, pid 1025.' in line]
    assert stop
    current = runs['201']['events']
    assert current['settings_start']['count'] == 1
    assert current['screen_unlock_2097253']['count'] >= 1
    assert current['default_account_activation']['count'] == 0
    assert runs['173']['events']['account100_storage_unlock']['count'] >= 1
    result = dict(runs=runs, candidate_account_stop=dict(
        path=fault.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(fault_data).hexdigest(),
        line_numbers=stop), target_modified=False, boot_executed=False,
        usb_work_resumed=False, raw_identity_or_token_values_exported=False,
        settings_window_verified=False,
        interpretation='Root CLI refusal is established; user100 UI failure cause remains unproven. '
        'Missing activation events are observations within these captures, not proof of missing accounts. '
        'Baseline also reports account startup errors; do not attribute Settings solely to account restart.')
    output.mkdir()
    with (output / 'result.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
