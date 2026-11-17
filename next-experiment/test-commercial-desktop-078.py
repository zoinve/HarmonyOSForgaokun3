"""Run the exact shell control flow with bounded public-command stand-ins."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess
import tempfile

b = Path(__file__).resolve().parent
module = runpy.run_path(str(b / 'commercial-init-desktop-078.py'))
script = module['SCRIPT']
out = b.parent / 'reports/commercial-desktop-test-078'
out.mkdir(exist_ok=False)
reference = Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816')
if not reference.exists():
    reference = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816')
original = (reference / 'ports/tests/native-desktop-start.sh').read_text()
for cmd in ['/system/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard',
            '/system/bin/aa force-stop com.huawei.hmos.hwstartupguide']:
    assert script.count(cmd) == original.count(cmd) == 1
scenarios = ['ready', 'missing-services', 'missing-marker', 'hilog-fails', 'restarted', 'expired', 'stop-fails-zero']
results = {}
with tempfile.TemporaryDirectory(prefix='desktop078-') as temporary:
    work = Path(temporary)
    for scenario in scenarios:
        folder = work / scenario
        folder.mkdir()
        uptime = folder / 'uptime'
        uptime.write_text('129.0 1.0\n' if scenario == 'expired' else '75.0 1.0\n')
        transformed = script.replace('/data/', str(folder) + '/').replace('/proc/uptime', str(uptime))
        transformed = transformed.replace('/system/bin/aurora/samgr-service-probe', 'probe078').replace(
            '/system/bin/grep', 'grep').replace('/system/bin/', 'mock078 ')
        prefix = r'''
stopped078=0
generation078=0
probe078() { [ "$scenario078" != missing-services ]; }
mock078() {
 name078="$1"; shift
 case "$name078" in
  id|hidumper) return 0 ;;
  cat) command cat "$@" ;;
  sleep)
   if [ "$scenario078" = restarted ] && [ "$1" = 2 ]; then generation078=1; fi
   return 0 ;;
  pidof)
   if [ "$1" = com.huawei.hmos.hwstartupguide ]; then
    [ "$stopped078" -eq 0 ] || return 1
    printf '333\n'
   elif [ "$generation078" -eq 0 ]; then printf '111\n'; else printf '222\n'; fi
   return 0 ;;
  hilog)
   [ "$scenario078" != hilog-fails ] || return 7
   [ "$scenario078" != missing-marker ] || return 0
   printf 'ResidentLayoutCacheMgr: getResidentList send EVENT_SMARTDOCK_INIT_FINISHED\n'
   return 0 ;;
  aa)
   printf 'MOCK_AA %s\n' "$*"
   if [ "$1" = force-stop ]; then
    if [ "$scenario078" = stop-fails-zero ]; then
     printf 'error: failed to force stop process.\n'; return 0
    fi
    stopped078=1
    printf 'force stop process successfully.\n'
   else printf 'start ability successfully.\n'; fi
   return 0 ;;
 esac
 return 127
}
'''
        process = subprocess.run(['sh', '-c', prefix + '\nscenario078=' + scenario + '\n' + transformed],
                                 capture_output=True, text=True, timeout=10)
        log = (folder / 'commercial-direct-desktop075.log').read_text()
        (out / (scenario + '.log')).open('x').write(log)
        results[scenario] = dict(returncode=process.returncode, sha256=hashlib.sha256(log.encode()).hexdigest())
        if scenario in ['ready', 'restarted']:
            assert process.returncode == 0 and 'force stop process successfully.' in log
            assert 'GUIDE_PID_RESULT result=1' in log
            pid = '222' if scenario == 'restarted' else '111'
            assert 'DOCK_READY scene_pid=' + pid in log
        elif scenario == 'stop-fails-zero':
            assert 'GUIDE_STOP_RESULT result=0' in log and 'error: failed to force stop process.' in log
            assert 'GUIDE_PID_RESULT result=0' in log and 'desktop_not_inferred=1' in log
        else:
            assert process.returncode == 1 and 'MOCK_AA force-stop' not in log
            assert 'READINESS_TIMEOUT' in log if scenario == 'missing-services' else 'DOCK_TIMEOUT' in log
result = dict(exact_shell_scenarios=results, current_pid_rechecked_after_marker=True,
              no_marker_no_stop=True, exit_zero_not_treated_as_success=True,
              reference_commands_preserved=True, script_sha256=hashlib.sha256(script.encode()).hexdigest(),
              runtime_verified=False)
(out / 'result.json').open('x').write(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
