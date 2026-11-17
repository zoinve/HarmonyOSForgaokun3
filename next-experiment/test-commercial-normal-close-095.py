"""Run the packaged shell worker against bounded off-device command fixtures."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

if __name__ == '__main__':
    report = ROOT/'reports/commercial61-native-095'
    out = report/'normal-close-shell-tests.json'
    assert not out.exists()
    script = (report/'normal-close095.sh').read_text()
    info = json.loads((report/'result.json').read_text())['normal_window_close_diagnostic']
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    full = Path('/home/zoinve/harmony-virgl-883/commercial61-native-095/initrd.img')
    members = {n: body for n, mode, body in parse(gzip.decompress(full.read_bytes()))}
    cases = {}
    with tempfile.TemporaryDirectory(prefix='normal-close-shell095-') as temporary:
        work = Path(temporary)
        busybox = work/'busybox'
        busybox.write_bytes(members['bin/busybox'])
        busybox.chmod(0o755)
        subprocess.run(['qemu-aarch64', str(busybox), 'sh', '-n', str(report/'normal-close095.sh')], check=True)
        for case in ('ready', 'desktop-focus', 'multiple-guides', 'missing-guide', 'bad-hash',
                     'dump-failed', 'scene-restarted', 'expired', 'invalid-table', 'helper-failed'):
            folder = work/case
            folder.mkdir()
            (folder/'uptime').write_text('129.0 1.0\n' if case == 'expired' else '125.0 1.0\n')
            header = 'WindowName DisplayId Pid WinId Type Mode Flag ZOrd Orientation\n'
            row = 'hwstartupguide0 0 6468 8 1 1 0 -1 0\n'
            focus = 'Focus window: 8\n'
            if case == 'desktop-focus':
                row += 'SCBDesktop4 0 4303 7 2001 1 0 -1 0\n'
                focus = 'Focus window: 7\n'
            if case == 'invalid-table':
                header = ''
            (folder/'windows').write_text(header+row+focus)
            transformed = script.replace('/proc/uptime', str(folder/'uptime')).replace('/data/', str(folder)+'/')
            transformed = transformed.replace('/commercial-focus095.awk', str(BASE/'commercial-focus-095.awk'))
            transformed = transformed.replace('/system/bin/awk', 'target_awk095').replace('/system/bin/', 'mock095 ')
            transformed = transformed.replace('\n/native-normal-close095 --send-once', '\nmock095 send-close --send-once')
            prefix = r'''
target_awk095() { qemu-aarch64 "$busybox095" awk "$@"; }
mock095() {
    name095="$1"; shift
    case "$name095" in
      sleep) printf '140.0 1.0\n' >| "$folder095/uptime" ;;
      cat) command cat "$@" ;;
      sha256sum)
        if [ "$case095" = bad-hash ]; then printf 'bad\n'
        elif [ "$1" = /native-normal-close095 ]; then printf '%s  %s\n' "$helper_sha095" "$1"
        else printf '%s  %s\n' "$focus_sha095" "$1"; fi ;;
      pidof)
        if [ "$1" = com.ohos.sceneboard ]; then
          if [ "$case095" = scene-restarted ] && [ -f "$folder095/scene-seen" ]; then printf '4304\n'
          else printf '4303\n'; : >| "$folder095/scene-seen"; fi
        elif [ "$case095" = multiple-guides ]; then printf '6468 7777\n'
        elif [ "$case095" = missing-guide ]; then return 1
        else printf '6468\n'; fi ;;
      timeout) shift; "$@" ;;
      hidumper)
        [ "$case095" != dump-failed ] || return 7
        command cat "$folder095/windows" ;;
      send-close)
        printf 'FIXTURE095_SEND_ONCE\n'
        [ "$case095" != helper-failed ] || return 66 ;;
      *) return 127 ;;
    esac
}
'''
            env = dict(__import__('os').environ, busybox095=str(busybox), folder095=str(folder),
                       case095=case, helper_sha095=info['helper_sha256'], focus_sha095=info['focus_sha256'])
            process = subprocess.run(['busybox', 'sh', '-c', prefix+'\n'+transformed],
                                     env=env, capture_output=True, text=True, timeout=10)
            expected = case in ('ready', 'helper-failed')
            attempts = process.stdout.count('FIXTURE095_SEND_ONCE')
            assert attempts == int(expected), (case, process.stdout, process.stderr)
            assert ('NORMAL_CLOSE095_END' in process.stdout) == expected, case
            if not expected:
                assert process.returncode == 1 and 'NORMAL_CLOSE095_REFUSED' in process.stdout, case
            if case == 'helper-failed':
                assert 'exit_status=66 window_dismissal_not_inferred=1' in process.stdout
            cases[case] = dict(returncode=process.returncode, key_request_attempts=attempts,
                               stdout=process.stdout, stderr=process.stderr)
    result = dict(worker_sha256=hashlib.sha256(script.encode()).hexdigest(), scenarios=cases,
                  window_guard_exercised_with_target_busybox=True,
                  target_keyboard_opened=False, original_ohos_elf_executed=False,
                  target_booted=False, runtime_success_not_inferred=True)
    out.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(scenarios=len(cases), all_passed=True, target_keyboard_opened=False)))
