#!/system/bin/sh
set -u
umask 077
set -C
exec > /data/commercial-server-stack105.log 2>&1 || exit 1
printf 'SERVER105_BEGIN single_capture=1 original_dfx=1 recovery_unchanged=1\n'
/system/bin/cat /proc/uptime
hash105=$(/system/bin/sha256sum /reference-stack-probe103 2>/dev/null || :)
if [ "$hash105" != 'bc9f14107ebfb682311bf8c714f148df579141bb443a358ff85199cdc443b181  /reference-stack-probe103' ]; then
    printf 'SERVER105_REFUSED reason=probe_hash\n'
    exit 1
fi
guide105=''
for poll105 in $(/system/bin/seq 1 120); do
    guide105=$(/system/bin/pidof com.huawei.hmos.hwstartupguide 2>/dev/null || :)
    [ -n "$guide105" ] && break
    /system/bin/sleep 1
done
case "$guide105" in
    ''|*[!0-9]*) printf 'SERVER105_REFUSED reason=guide_not_unique\n'; exit 1 ;;
esac
printf 'SERVER105_GUIDE_FIRST pid=%s\n' "$guide105"
/system/bin/cat /proc/uptime
/system/bin/sleep 5
server105=$(/system/bin/pidof CollaborationFwk 2>/dev/null || :)
scene105=$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)
case "$server105" in
    ''|*[!0-9]*|0|1) printf 'SERVER105_REFUSED reason=server_not_unique\n'; exit 1 ;;
esac
printf 'SERVER105_CAPTURE_BEGIN server_pid=%s scene_pids=%s guide_first_pid=%s\n' "$server105" "$scene105" "$guide105"
/system/bin/cat /proc/uptime
printf 'SERVER105_DFX_CALL_BEGIN\n'
/system/bin/timeout 12 /reference-stack-probe103 "$server105" all
status105=$?
printf 'SERVER105_CAPTURE_END status=%s success_not_inferred=1\n' "$status105"
/system/bin/cat /proc/uptime
printf 'SERVER105_TASK_SURVEY_BEGIN post_capture_only=1\n'
for task105 in /proc/"$server105"/task/[0-9]*; do
    [ -d "$task105" ] || continue
    printf 'SERVER105_TASK tid=%s\n' "${task105##*/}"
    for kind105 in comm wchan syscall; do
        printf 'SERVER105_TASK_FILE kind=%s\n' "$kind105"
        /system/bin/cat "$task105/$kind105" || :
        printf '\n'
    done
done
printf 'SERVER105_TASK_SURVEY_END\n'
/system/bin/cat /proc/uptime
current105=$(/system/bin/pidof CollaborationFwk 2>/dev/null || :)
printf 'SERVER105_SERVER_AFTER pids=%s same_pid=%s\n' "$current105" "$([ "$current105" = "$server105" ] && printf 1 || printf 0)"
printf 'SERVER105_END desktop_not_inferred=1\n'
