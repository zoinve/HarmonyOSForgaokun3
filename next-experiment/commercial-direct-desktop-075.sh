#!/system/bin/sh
set -u
umask 077
set -C
exec > /data/commercial-direct-desktop075.log 2>&1 || exit 1
printf 'COMMERCIAL075_BEGIN activation_state_not_modified=1\n'
/system/bin/id
/system/bin/cat /proc/self/attr/current
n=0
while [ "$n" -lt 110 ]; do
    if /system/bin/aurora/samgr-service-probe 401 501 4606 4607 >/dev/null 2>&1 &&
       /system/bin/pidof com.ohos.sceneboard >/dev/null 2>&1 &&
       /system/bin/pidof com.huawei.hmos.hwstartupguide >/dev/null 2>&1; then
        break
    fi
    n=$((n + 1))
    /system/bin/sleep 1
done
if [ "$n" -ge 110 ]; then
    printf 'COMMERCIAL075_READINESS_TIMEOUT no_stop_requested=1\n'
    exit 1
fi
/system/bin/cat /proc/uptime
/system/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard
printf 'COMMERCIAL075_START_RESULT result=%s\n' "$?"
/system/bin/sleep 10
if ! /system/bin/pidof com.huawei.hmos.hwstartupguide >/dev/null 2>&1; then
    printf 'COMMERCIAL075_GUIDE_GONE no_stop_requested=1\n'
    exit 1
fi
/system/bin/aa force-stop com.huawei.hmos.hwstartupguide
printf 'COMMERCIAL075_GUIDE_STOP_RESULT result=%s\n' "$?"
/system/bin/sleep 3
/system/bin/cat /proc/uptime
/system/bin/pidof com.ohos.sceneboard
printf 'COMMERCIAL075_SCENE_PID_RESULT result=%s\n' "$?"
/system/bin/pidof com.huawei.hmos.hwstartupguide
printf 'COMMERCIAL075_GUIDE_PID_RESULT result=%s\n' "$?"
/system/bin/aa dump -e -u 100
/system/bin/hidumper -s 4606 -a -a
printf 'COMMERCIAL075_COMMANDS_DONE desktop_not_inferred=1\n'
