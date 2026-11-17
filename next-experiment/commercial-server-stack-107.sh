#!/system/bin/sh
set -u
umask 077
set -C
exec > /data/commercial-server-stack107.log 2>&1 || exit 1
printf 'SERVER107_BEGIN event_triggered=1 original_dfx=1 recovery_unchanged=1\n'
/system/bin/cat /proc/uptime
hash107=$(/system/bin/sha256sum /reference-stack-probe103 2>/dev/null || :)
if [ "$hash107" != 'bc9f14107ebfb682311bf8c714f148df579141bb443a358ff85199cdc443b181  /reference-stack-probe103' ]; then
    printf 'SERVER107_REFUSED reason=probe_hash\n'
    exit 1
fi
scene107=''
for poll107 in $(/system/bin/seq 1 120); do
    scene107=$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)
    [ -n "$scene107" ] && break
    /system/bin/sleep 1
done
case "$scene107" in
    ''|*[!0-9]*|0|1) printf 'SERVER107_REFUSED reason=scene_not_unique\n'; exit 1 ;;
esac
fifo107=/data/commercial-query107.fifo
/system/bin/mkfifo "$fifo107" || exit 1
reader107=''
cleanup107()
{
    if [ -n "$reader107" ]; then
        kill -KILL "$reader107" 2>/dev/null || :
        wait "$reader107" 2>/dev/null || :
        reader107=''
    fi
    /system/bin/rm -f "$fifo107"
}
trap cleanup107 0
trap 'exit 1' 1 2 15
/system/bin/hilog > "$fifo107" 2>/dev/null &
reader107=$!
pattern107="[[:space:]]${scene107}[[:space:]]+${scene107}[[:space:]]+I[[:space:]]+.*CFWKProxy: .*GetTrustedDeviceListWithAbilityFilter# start"
event107=$(/system/bin/timeout 90 /system/bin/grep -E -m 1 "$pattern107" "$fifo107")
trigger_status107=$?
cleanup107
trap - 0 1 2 15
if [ "$trigger_status107" -ne 0 ] || [ -z "$event107" ]; then
    printf 'SERVER107_REFUSED reason=query_event_missing status=%s\n' "$trigger_status107"
    exit 1
fi
printf 'SERVER107_QUERY_EVENT %s\n' "$event107"
/system/bin/cat /proc/uptime
current107=$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)
[ "$current107" = "$scene107" ] || { printf 'SERVER107_REFUSED reason=scene_changed\n'; exit 1; }
dm107=$(/system/bin/pidof device_manager 2>/dev/null || :)
server107=$(/system/bin/pidof CollaborationFwk 2>/dev/null || :)
for target107 in "$dm107" "$server107"; do
    case "$target107" in
        ''|*[!0-9]*|0|1) printf 'SERVER107_REFUSED reason=target_not_unique\n'; exit 1 ;;
    esac
done
for role107 in device_manager CollaborationFwk; do
    case "$role107" in device_manager) target107=$dm107 ;; *) target107=$server107 ;; esac
    printf 'SERVER107_DFX_CALL_BEGIN role=%s pid=%s scene_pid=%s\n' "$role107" "$target107" "$scene107"
    /system/bin/cat /proc/uptime
    /system/bin/timeout 12 /reference-stack-probe103 "$target107" all
    status107=$?
    printf 'SERVER107_DFX_CALL_END role=%s status=%s success_not_inferred=1\n' "$role107" "$status107"
    /system/bin/cat /proc/uptime
done
printf 'SERVER107_END desktop_not_inferred=1\n'
