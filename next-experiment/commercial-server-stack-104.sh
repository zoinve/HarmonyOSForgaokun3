#!/system/bin/sh
set -u
umask 077
set -C
exec > /data/commercial-server-stack104.log 2>&1 || exit 1
printf 'SERVER104_BEGIN single_capture=1 original_dfx=1 recovery_unchanged=1\n'
/system/bin/cat /proc/uptime
hash104=$(/system/bin/sha256sum /reference-stack-probe103 2>/dev/null || :)
if [ "$hash104" != 'bc9f14107ebfb682311bf8c714f148df579141bb443a358ff85199cdc443b181  /reference-stack-probe103' ]; then
    printf 'SERVER104_REFUSED reason=probe_hash\n'
    exit 1
fi
guide104=''
for poll104 in $(/system/bin/seq 1 120); do
    guide104=$(/system/bin/pidof com.huawei.hmos.hwstartupguide 2>/dev/null || :)
    [ -n "$guide104" ] && break
    /system/bin/sleep 1
done
case "$guide104" in
    ''|*[!0-9]*) printf 'SERVER104_REFUSED reason=guide_not_unique\n'; exit 1 ;;
esac
printf 'SERVER104_GUIDE_FIRST pid=%s\n' "$guide104"
/system/bin/cat /proc/uptime
/system/bin/sleep 5
server104=$(/system/bin/pidof CollaborationFwk 2>/dev/null || :)
scene104=$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)
case "$server104" in
    ''|*[!0-9]*|0|1) printf 'SERVER104_REFUSED reason=server_not_unique\n'; exit 1 ;;
esac
printf 'SERVER104_CAPTURE_BEGIN server_pid=%s scene_pids=%s guide_first_pid=%s\n' "$server104" "$scene104" "$guide104"
/system/bin/cat /proc/uptime
for task104 in /proc/"$server104"/task/[0-9]*; do
    [ -d "$task104" ] || continue
    printf 'SERVER104_TASK tid=%s\n' "${task104##*/}"
    for kind104 in comm wchan syscall; do
        printf 'SERVER104_TASK_FILE kind=%s\n' "$kind104"
        /system/bin/cat "$task104/$kind104" || :
        printf '\n'
    done
done
/system/bin/timeout 12 /reference-stack-probe103 "$server104" all
status104=$?
printf 'SERVER104_CAPTURE_END status=%s success_not_inferred=1\n' "$status104"
/system/bin/cat /proc/uptime
current104=$(/system/bin/pidof CollaborationFwk 2>/dev/null || :)
printf 'SERVER104_SERVER_AFTER pids=%s same_pid=%s\n' "$current104" "$([ "$current104" = "$server104" ] && printf 1 || printf 0)"
printf 'SERVER104_END desktop_not_inferred=1\n'
