#!/system/bin/sh
set -u
umask 077
set -C
exec > /data/commercial-desktop086.log 2>&1 || exit 1
printf 'LAYOUT086_BEGIN original_tool=1 no_input_injected=1 original_service_permissions_unchanged=1\n'
/system/bin/id
/system/bin/cat /proc/self/attr/current
if [ ! -x /system/bin/uitest ] || [ ! -x /system/bin/timeout ]; then
    printf 'LAYOUT086_TOOL_MISSING no_substitute=1\n'
    exit 1
fi
for target086 in 100 130; do
    while :; do
        IFS=' ' read -r uptime086 rest086 < /proc/uptime
        seconds086=${uptime086%%.*}
        [ "$seconds086" -ge "$target086" ] && break
        /system/bin/sleep 1
    done
    printf 'LAYOUT086_ATTEMPT target=%s\n' "$target086"
    /system/bin/cat /proc/uptime
    /system/bin/pidof com.ohos.sceneboard com.huawei.hmos.hwstartupguide || :
    /system/bin/timeout 8 /system/bin/uitest dumpLayout -p "/data/native-layout086-$target086.json"
    status086=$?
    printf 'LAYOUT086_RESULT target=%s exit_status=%s success_not_inferred=1\n' "$target086" "$status086"
done
printf 'LAYOUT086_END desktop_not_inferred=1\n'
