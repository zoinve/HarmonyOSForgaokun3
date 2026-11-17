#!/system/bin/sh
set -u
umask 077
set -C
exec > /data/commercial-desktop086.log 2>&1 || exit 1
printf 'DESKTOP089_BEGIN single_original_force_stop=1 provisioning_unchanged=1\n'
/system/bin/id
/system/bin/cat /proc/self/attr/current
ready089=''
while :; do
    IFS=' ' read -r uptime089 rest089 < /proc/uptime
    seconds089=${uptime089%%.*}
    [ "$seconds089" -ge 105 ] && break
    scenes089=$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)
    case "$scenes089" in ''|*[!0-9]*) /system/bin/sleep 1; continue ;; esac
    if [ "$seconds089" -lt 65 ]; then
        /system/bin/sleep 1
        continue
    fi
    probe089="/data/desktop089-ready-$seconds089-$scenes089.log"
    if /system/bin/timeout 3 /system/bin/hilog -x -P "$scenes089" -e EVENT_SMARTDOCK_INIT_FINISHED > "$probe089" 2>&1 &&
       /system/bin/grep -F -q 'ResidentLayoutCacheMgr: getResidentList send EVENT_SMARTDOCK_INIT_FINISHED' "$probe089"; then
        /system/bin/sleep 10
        current089=$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)
        if [ "$current089" = "$scenes089" ]; then
            ready089="$scenes089"
            /system/bin/cat "$probe089"
            break
        fi
        printf 'DESKTOP089_SCENE_CHANGED before=%s after=%s no_stop_requested=1\n' "$scenes089" "$current089"
    fi
    /system/bin/sleep 1
done
if [ -z "$ready089" ]; then
    printf 'DESKTOP089_DOCK_TIMEOUT no_stop_requested=1\n'
else
    printf 'DESKTOP089_DOCK_READY scene_pid=%s stable_interval=10\n' "$ready089"
    guide089=$(/system/bin/pidof com.huawei.hmos.hwstartupguide 2>/dev/null || :)
    if [ -n "$guide089" ]; then
        printf 'DESKTOP089_STOP_BEGIN guide_pids=%s scene_pid=%s\n' "$guide089" "$ready089"
        /system/bin/timeout 8 /system/bin/aa force-stop com.huawei.hmos.hwstartupguide
        status089=$?
        printf 'DESKTOP089_STOP_RESULT exit_status=%s success_not_inferred=1\n' "$status089"
    else
        printf 'DESKTOP089_GUIDE_ABSENT no_stop_requested=1\n'
    fi
fi
for target089 in 100 130; do
    while :; do
        IFS=' ' read -r uptime089 rest089 < /proc/uptime
        seconds089=${uptime089%%.*}
        [ "$seconds089" -ge "$target089" ] && break
        /system/bin/sleep 1
    done
    printf 'DESKTOP089_SAMPLE target=%s ready_pid=%s\n' "$target089" "$ready089"
    /system/bin/cat /proc/uptime
    printf 'DESKTOP089_SCENE_PIDS '
    /system/bin/pidof com.ohos.sceneboard || :
    printf '\nDESKTOP089_GUIDE_PIDS '
    /system/bin/pidof com.huawei.hmos.hwstartupguide || :
    printf '\nLAYOUT086_ATTEMPT target=%s\n' "$target089"
    /system/bin/timeout 8 /system/bin/uitest dumpLayout -p "/data/native-layout086-$target089.json"
    printf 'LAYOUT086_RESULT target=%s exit_status=%s success_not_inferred=1\n' "$target089" "$?"
done
printf 'DESKTOP089_END desktop_not_inferred=1\n'
