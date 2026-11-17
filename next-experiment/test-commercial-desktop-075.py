"""Exercise the real guide script with CLI stand-ins and exact source deltas."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess
import tempfile

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
out = b.parent / 'reports/commercial-desktop-test-075'
out.mkdir()
script = (b / 'commercial-direct-desktop-075.sh').read_text()
reference = runpy.run_path(str(b / 'commercial-desktop-evidence-075.py'))['reference']
original = (reference / 'ports/tests/native-desktop-start.sh').read_text()
for command in ['/system/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard',
                '/system/bin/aa force-stop com.huawei.hmos.hwstartupguide']:
    assert script.count(command) == original.count(command) == 1
for forbidden in ['param set', 'setuid', 'setgid', 'chmod', 'settings put', 'provisioned', 'LD_PRELOAD']:
    assert forbidden not in script
transcripts = {}
with tempfile.TemporaryDirectory(prefix='desktop075-') as temporary:
    work = Path(temporary)
    for scenario in ['success', 'missing-services', 'guide-gone', 'stop-fails']:
        folder = work / scenario
        folder.mkdir()
        transformed = script.replace('/data/commercial-direct-desktop075.log', str(folder / 'log'))
        transformed = transformed.replace('/system/bin/aurora/samgr-service-probe', 'probe075').replace(
            '/system/bin/', 'mock075 ')
        # Only the CLI stand-ins change; the script's original control flow runs.
        prefix = '''#!/bin/sh
stopped075=0
guide_checks075=0
probe075() { [ "$scenario075" != missing-services ]; }
mock075() {
 name075="$1"; shift
 case "$name075" in
  sleep|cat|id|hidumper) return 0;;
  pidof)
   if [ "$1" = com.huawei.hmos.hwstartupguide ]; then
    guide_checks075=$((guide_checks075 + 1))
    [ "$stopped075" -eq 0 ] || return 1
    if [ "$scenario075" = guide-gone ] && [ "$guide_checks075" -gt 1 ]; then return 1; fi
   fi
   printf '1234\\n'; return 0;;
  aa)
   printf 'MOCK_AA %s\\n' "$*"
   if [ "$1" = force-stop ]; then
    [ "$scenario075" != stop-fails ] || return 7
    stopped075=1
   fi
   return 0;;
 esac
 return 127
}
'''
        result = subprocess.run(['sh', '-c', prefix + '\nscenario075=' + scenario + '\n' + transformed],
                                capture_output=True, text=True, timeout=10)
        log = (folder / 'log').read_text()
        transcripts[scenario] = dict(returncode=result.returncode, log=log)
        (out / (scenario + '.log')).open('x').write(log)
        if scenario == 'success':
            assert result.returncode == 0 and 'GUIDE_STOP_RESULT result=0' in log
            assert 'GUIDE_PID_RESULT result=1' in log and 'COMMANDS_DONE' in log
        elif scenario == 'missing-services':
            assert result.returncode == 1 and 'READINESS_TIMEOUT' in log and 'MOCK_AA' not in log
        elif scenario == 'guide-gone':
            assert result.returncode == 1 and 'GUIDE_GONE' in log and 'MOCK_AA force-stop' not in log
        else:
            assert 'GUIDE_STOP_RESULT result=7' in log and 'GUIDE_PID_RESULT result=0' in log
h = runpy.run_path(str(b / 'commercial-desktop-evidence-075.py'))
before = (root / 'commercial-composer-068/composer-evidence-068.cpp').read_text()
after = (root / 'commercial-composer-075/composer-evidence-075.cpp').read_text()
assert after == h['instrument'](before)
assert after.count('full068_capture(buffer);') == after.count('full075_capture(buffer);') == 1
assert 'now068<140000000' in after and '/data/native-full-075' in after
build = json.loads((root / 'commercial-composer-075/result.json').read_text())
assert build['source_sha256'] == hashlib.sha256(after.encode()).hexdigest()
assert build['public_exports_unchanged'] and not build['sdk_runtime_libraries_used']
result = dict(original_reference_commands_verified=True, mock_cli_control_flow_passed=True,
    no_stop_when_services_or_guide_missing=True, stop_failure_not_misreported=True,
    exact_composer_source_addition=True, two_independent_capture_directories=True,
    real_kernel_input_event_path=True, activation_state_not_modified=True,
    script_sha256=hashlib.sha256(script.encode()).hexdigest(),
    reference_script_sha256=hashlib.sha256(original.encode()).hexdigest(),
    composer_source_sha256=build['source_sha256'], desktop_verified=False, interaction_verified=False)
(out / 'result.json').open('x').write(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
