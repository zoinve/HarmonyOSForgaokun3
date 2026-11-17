"""Correlate verified seed loading with original first-run and process behavior."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'next-experiment'

if __name__ == '__main__':
    folder = ROOT / 'reports/commercial61-native-123'
    output = folder / 'oobe-seed-runtime-analysis.json'
    assert not output.exists()
    manifest = json.loads((folder / 'runtime-evidence/retrieval-manifest.json').read_text())
    verified = {}
    def load(name):
        raw = (folder / 'runtime-evidence/raw' / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == manifest['files'][name]['sha256']
        assert len(raw) == manifest['files'][name]['bytes']
        verified[name] = manifest['files'][name]['sha256']
        return raw
    log = load('interactive-hilog030.log')
    phase_name = max((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log', n)),
                     key=lambda n: int(n.split('-')[1].split('.')[0]))
    phase = load(phase_name)
    sanitize = runpy.run_path(str(BASE / 'analyze-original-devicedetect-095.py'))['sanitize']
    original = []
    scene, guide = [], []
    for number, line in enumerate(log.splitlines(), 1):
        if len(line) >= 4096:
            continue
        match = re.search(rb'Child process (com.ohos.sceneboard|com.huawei.hmos.hwstartupguide) success pid (\d+)', line)
        if match:
            row = dict(line=number, pid=int(match.group(2)), text=sanitize(line))
            (scene if match.group(1) == b'com.ohos.sceneboard' else guide).append(row)
        if any(marker in line for marker in (b'SCBOobeManager:', b'OobePreferences_OobeManager:',
                b'BaseOobeManager: sessionExceptionCallback', b'BaseOobeManager: start oobe again',
                b'BaseOobeManager: getSecureUri', b'OtaOobeManager:')):
            original.append(dict(line=number, text=sanitize(line)))
    reference = load('snapshot075-commercial-direct-desktop075.log') if 'snapshot075-commercial-direct-desktop075.log' in manifest['files'] else b''
    result = dict(run=manifest['run'], verified_input_sha256=verified,
        seed_verified_marker_observed=b'OOBE123_SEED_VERIFIED original_images_unchanged=1 local_setup_flags=1 commercial_activation_unchanged=1' in phase,
        original_init_observed_provisioned_one_inactive=(b'init ok, provisioned: 1, isOobeEnable: false' in log),
        original_secure_setting_one_observed=(b'user_setup_complete is 1' in log),
        original_oobe_lifecycle=original, scene_launches=scene, guide_launches=guide,
        guide_creation_not_observed=(not guide),
        original_recovery_restart_observed=b'BaseOobeManager: start oobe again' in log,
        original_reference_stop_succeeded=b'force stop process successfully' in reference,
        original_reference_samples_present=b'REFERENCE099_SAMPLE target=' in reference,
        missing_reference_samples_not_guide_absence_proof=True,
        reference_helper_may_wait_beyond_budget_if_no_guide=True,
        final_phase=phase_name,
        bounded_exit_records=[sanitize(line) for line in phase.splitlines() if
            re.search(rb'COMMERCIAL087_TARGET_EXIT|COMMERCIAL087 target_timeout|NATIVE_ORIGINAL_END|NATIVE_DIAGNOSTIC_END', line)],
        setup_flags_user_authorized=True, commercial_activation_verified=False,
        desktop_verified=False, interaction_verified=False,
        original_state_and_process_logs_not_pixel_acceptance=True)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
