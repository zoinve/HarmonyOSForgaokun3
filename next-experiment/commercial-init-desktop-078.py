"""Dismiss the guide only after this live SceneBoard completed Dock init."""
from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-init-desktop-077.py'))
GATE = r'''
ready078=''
poll078=0
while [ "$poll078" -lt 120 ]; do
    IFS=' ' read -r uptime078 rest078 < /proc/uptime
    seconds078=${uptime078%%.*}
    if [ "$seconds078" -ge 128 ]; then
        break
    fi
    candidates078=$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)
    for scene078 in $candidates078; do
        case "$scene078" in ''|*[!0-9]*) continue ;; esac
        probe078="/data/commercial-desktop078-ready-$poll078-$scene078.log"
        if /system/bin/hilog -x -P "$scene078" -e EVENT_SMARTDOCK_INIT_FINISHED > "$probe078" 2>&1 &&
           /system/bin/grep -F -q 'ResidentLayoutCacheMgr: getResidentList send EVENT_SMARTDOCK_INIT_FINISHED' "$probe078"; then
            /system/bin/sleep 2
            candidates078=$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)
            case " $candidates078 " in
                *" $scene078 "*)
                    ready078="$scene078"
                    /system/bin/cat "$probe078"
                    break 2 ;;
            esac
        fi
    done
    poll078=$((poll078 + 1))
    /system/bin/sleep 1
done
if [ -z "$ready078" ]; then
    printf 'COMMERCIAL078_DOCK_TIMEOUT no_stop_requested=1\n'
    exit 1
fi
printf 'COMMERCIAL078_DOCK_READY scene_pid=%s original_hilog_marker=1\n' "$ready078"
'''
SCRIPT = previous['SCRIPT'].replace('COMMERCIAL077', 'COMMERCIAL078')
anchor = 'if ! /system/bin/pidof com.huawei.hmos.hwstartupguide'
assert SCRIPT.count(anchor) == 1
SCRIPT = SCRIPT.replace(anchor, GATE + '\n' + anchor, 1)
CONFIG = dict(services=[dict(previous['CONFIG']['services'][0], name='matebook_desktop078')])


def update_config(body):
    original = json.loads(body)
    assert not any(s['name'].startswith('matebook_desktop') for s in original['services'])
    return (json.dumps(dict(original, services=original['services'] + CONFIG['services']), indent=2) + '\n').encode()
