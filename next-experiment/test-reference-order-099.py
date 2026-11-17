"""Exercise reference ordering without replacing its shell control flow."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent


if __name__ == '__main__':
    output = ROOT/'reports/reference-order-099-tests.json'
    assert not output.exists()
    builder = runpy.run_path(str(BASE/'build-commercial-native-099.py'))
    original, adapted = builder['reference_script']()
    observer = (BASE/'commercial-reference-observer-099.sh').read_bytes()
    assert adapted.count(b'/system/bin/aa force-stop ') == 1
    assert observer.count(b'/system/bin/sh /harmonymac-reference099.sh') == 1
    assert b'force-stop' not in observer
    for forbidden in (b'param set', b'setuid', b'setgid', b'settings put', b'LD_PRELOAD', b'kill '):
        assert forbidden not in adapted + observer
    prefix = '''#!/bin/sh
probes099=0
guide099=0
started099=0
mkdir() { :; }
cat() { printf 'TEST_UPTIME\\n'; }
sleep() { printf 'sleep %s\\n' "$*" >> "$events099"; }
probe099() {
 probes099=$((probes099+1))
 printf 'probe %s\\n' "$probes099" >> "$events099"
 [ "$scenario099" != missing-services ] || return 1
 [ "$scenario099" != delayed-services ] || [ "$probes099" -ge 3 ]
}
pidof() {
 printf 'pidof %s\\n' "$*" >> "$events099"
 [ "$started099" -eq 1 ] || return 9
 guide099=$((guide099+1))
 [ "$scenario099" != missing-guide ] || return 1
 [ "$scenario099" != delayed-guide ] || [ "$guide099" -ge 3 ] || return 1
 printf '1234\\n'
}
aa099() {
 printf 'aa %s\\n' "$*" >> "$events099"
 if [ "$1" = start ]; then
  started099=1
  [ "$scenario099" != start-fails ] || return 7
 else
  [ "$scenario099" != stop-fails ] || return 8
 fi
}
dump099() { printf 'TEST_DUMP\\n'; }
'''
    cases = {}
    with tempfile.TemporaryDirectory(prefix='reference099-') as temporary:
        for scenario in ('success', 'delayed-services', 'delayed-guide', 'missing-services',
                         'missing-guide', 'start-fails', 'stop-fails'):
            folder = Path(temporary)/scenario
            folder.mkdir()
            source = adapted.decode().replace('/data/commercial-direct-desktop075.log', str(folder/'log')).replace(
                '/system/bin/aurora/samgr-service-probe', 'probe099').replace('/system/bin/aa', 'aa099').replace(
                '/system/bin/hidumper', 'dump099')
            command = prefix + '\nscenario099='+scenario+'\nevents099='+str(folder/'events')+'\n'+source
            result = subprocess.run(['sh', '-c', command], capture_output=True, timeout=5)
            events = (folder/'events').read_text().splitlines()
            starts = [i for i, line in enumerate(events) if line.startswith('aa start ')]
            stops = [i for i, line in enumerate(events) if line.startswith('aa force-stop ')]
            pids = [i for i, line in enumerate(events) if line.startswith('pidof ')]
            assert result.returncode == 0
            assert len(starts) == 1 and starts[0] < pids[0]
            assert len(stops) == (0 if scenario == 'missing-guide' else 1)
            if stops:
                assert events[stops[0]-1] == 'sleep 10'
            if scenario == 'missing-services':
                assert len([e for e in events if e.startswith('probe ')]) == 120
            if scenario == 'missing-guide':
                assert len(pids) == 180
            assert 'NATIVE_DESKTOP_READY' in (folder/'log').read_text()
            cases[scenario] = dict(events=events, exit_status=result.returncode,
                                  marker_is_not_success_evidence=True)
    sha = lambda b: hashlib.sha256(b).hexdigest()
    result = dict(reference_sha256=sha(original), adapted_sha256=sha(adapted), observer_sha256=sha(observer),
                  all_scenarios_passed=True, original_timeout_and_failure_behavior_preserved=True,
                  scene_start_precedes_first_guide_probe=True, no_repeated_force_stop=True,
                  scenarios=cases, native_runtime_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'scenarios'}, indent=2))
