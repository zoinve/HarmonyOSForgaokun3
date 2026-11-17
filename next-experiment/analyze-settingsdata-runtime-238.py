"""Compare original provider/SceneBoard events without inferring a usable UI."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
OPEN = runpy.run_path(str(Path(__file__).with_name('compress-historical-logs-226.py')))['open_log']
PATTERNS = {
    'provider_missing_el1_base': r'com\.ohos\.settingsdata/APPSPAWN:.*check dir /data/app/el1/0/base/com\.ohos\.settingsdata failed',
    'provider_sandbox_base_failure': r'com\.ohos\.settingsdata/APPSPAWN:.*DoAppSandboxMountOnce section app-base failed',
    'provider_sandbox_property_failure': r'com\.ohos\.settingsdata/APPSPAWN:.*SetSandboxProperty failed',
    'provider_restorecon_missing_base': r'HapFileRestorecon fail for path:.*app/el1/0/base/com\.ohos\.settingsdata',
    'provider_creation_markers': r'com\.ohos\.settingsdata/.*(?:onCreate|OnCreate)',
    'provider_data_ability_references': r'com\.ohos\.settingsdata\.DataAbility',
    'sceneboard_watchdog_reboot': r'panic:SceneBoard exits',
    'settings_launch_requests': r'StartAbility ability:com\.huawei\.hmos\.settings/',
    'settings_background_extension_created': r'SettingsExtServiceAbility.*onCreate',
    'settings_main_ability_name_references': r'com\.huawei\.hmos\.settings\.MainAbility',
    'root_cli_request_markers': r'SETTINGS206_REQUEST|SETTINGS235_REQUEST',
}


def events(text):
    result = {name: dict(count=0, first_line=None, last_line=None) for name in PATTERNS}
    patterns = {name: re.compile(value) for name, value in PATTERNS.items()}
    for number, line in enumerate(text.splitlines(), 1):
        for name, pattern in patterns.items():
            if pattern.search(line):
                row = result[name]
                row['count'] += 1
                row['first_line'] = row['first_line'] or number
                row['last_line'] = number
    return result


def analyze(revision):
    folder = ROOT / 'reports' / ('commercial61-native-' + revision)
    manifest = json.loads((folder / 'runtime-evidence/retrieval-manifest.json').read_text())
    for name, metadata in manifest['files'].items():
        assert '/' not in name and '\\' not in name and name not in ['.', '..']
        with OPEN(folder / 'runtime-evidence/raw' / name) as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == metadata['sha256']
    with OPEN(folder / 'runtime-evidence/raw/interactive-hilog030.log') as stream:
        hilog = stream.read().decode(errors='replace')
    phases = sorted((name for name in manifest['files'] if re.fullmatch(r'phase-[0-9]+\.log', name)),
                    key=lambda name: int(name[6:-4]))
    assert phases
    with OPEN(folder / 'runtime-evidence/raw' / phases[-1]) as stream:
        phase = stream.read().decode(errors='replace')
    return dict(run=manifest['run'], all_retrieved_member_hashes_verified=True,
        retained_phase_files=len(phases), events=events(hilog),
        target_survived_until_harness_timeout='COMMERCIAL087 target_timeout=1\n' in phase,
        native_namespace_pins=len(re.findall(r'^PERSISTENT172_PIN target=\d+ data_identity_verified=1$', phase, re.M)),
        native_flushes=len(re.findall(r'^PERSISTENT172_FLUSHED target_reaped=1 .*remaining_data_mounts=0', phase, re.M)),
        pin_refusal_events=len(re.findall(r'^PERSISTENT172_PIN_REFUSED ', phase, re.M)),
        original_services_graceful_shutdown_verified=False, settings_window_verified=False,
        absent_events_not_nonexecution_proof=True)


if __name__ == '__main__':
    output = ROOT / 'reports/settingsdata-runtime-comparison-238.json'
    assert not output.exists()
    result = dict(runs={revision: analyze(revision) for revision in ['206', '235']},
        target_modified=False, usb_work_resumed=False, settings_ui_acceptance_complete=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
