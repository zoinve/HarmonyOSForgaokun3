"""Correlate genuine BMS/account/CLI evidence; never infer UI from registration."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parent.parent
PATTERNS={
    'bms_registered401': 'insert SA:401_',
    'bms_start_completed': 'BMSEventHandler AfterBmsStart end',
    'bms_main_ready_write': 'SystemSetParameter name bootevent.bms.main.bundles.ready ',
    'account_received_bms401': 'OnAddSystemAbility systemAbilityId 401',
    'default_account_activation': 'Start to activate default account',
    'account100_storage_unlock': 'OS account:100 is unlocked.',
    'account100_ams_start': 'Start OS account 100',
    'account100_callback_success': 'OnStartUserDone id is 100, errcode is 0.',
    'settings_start': 'StartAbility com.huawei.hmos.settings/com.huawei.hmos.settings.MainAbility',
    'first_unlock_refusal': 'no startup before device first unlock',
    'screen_unlock_2097253': 'DoProcess err: ScreenUnlock_2097253',
    'user0_default_locked': 'userId=0, default screenLocked: true',
}


def inspect(number):
    report=ROOT/('reports/commercial61-native-'+number)
    evidence=report/'runtime-evidence'
    manifest=json.loads((evidence/'retrieval-manifest.json').read_text())
    for name,row in manifest['files'].items():
        data=(evidence/'raw'/name).read_bytes()
        assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],name
    lines=(evidence/'raw/interactive-hilog030.log').read_text(errors='replace').splitlines()
    events={}
    for key,pattern in PATTERNS.items():
        found=[i for i,line in enumerate(lines,1) if pattern in line]
        events[key]=dict(count=len(found),first_line=found[0] if found else None,
                         last_line=found[-1] if found else None)
    pending=[];erased=[]
    for i,line in enumerate(lines,1):
        if 'HandlePreInstallException bundleName:' in line:pending.append(i)
        if 'exceptionBundleNames erase -n' in line:erased.append(i)
    return dict(run=manifest['run'],retrieved_files_hash_verified=len(manifest['files']),events=events,
        preinstall_recovery_starts=len(pending),preinstall_recovery_erase_events=len(erased),
        last_recovery_start_line=pending[-1] if pending else None,
        absent_events_not_nonexecution_proof=True)


def main():
    report=ROOT/'reports/settings-launch-209';assert not report.exists()
    runs={number:inspect(number) for number in ['173','197-r1','201','206']}
    cli=ROOT/'reports/commercial61-native-206/runtime-evidence/raw/settings206-start.log'
    text=cli.read_text() if cli.is_file() else ''
    readiness=[dict(bms=int(b),account=int(a),appfwk=int(f)) for b,a,f in re.findall(
        r'SETTINGS206_READINESS bms=(\d) account=(\d) appfwk=(\d) original_parameters_read_only=1',text)]
    requests=text.count('SETTINGS206_REQUEST ')
    assert requests<=1,'single-launch invariant violated'
    result=dict(runs=runs,cli_log_present=cli.is_file(),readiness_observations=readiness,
        actual_cli_launch_requests=requests,
        cli_errors=re.findall(r'Error Code:(\d+)',text),
        original_cli_exit_statuses=[int(value) for value in re.findall(r'SETTINGS206_AA_EXIT status=(\d+)',text)],
        cli_process_exit_not_semantic_success=True,settings_window_verified=False,
        desktop_frame_verified=False,target_modified_by_analyzer=False,usb_work_resumed=False)
    report.mkdir()
    with (report/'result.json').open('x') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
