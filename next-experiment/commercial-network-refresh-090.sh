#!/system/bin/sh
set -u
umask 077
set -C
exec > /data/commercial-desktop086.log 2>&1 || exit 1
printf 'REFRESH090_BEGIN real_wpa_cycle_once=1 no_guide_stop=1 provisioning_unchanged=1\n'
/system/bin/id
/system/bin/cat /proc/self/attr/current
printf '\n'
cli090() (
    case "$1" in status|disconnect|reconnect) ;; *) exit 64 ;; esac
    unset LD_PRELOAD LD_LIBRARY_PATH
    exec /system/bin/timeout 5 /network083/lib/ld-linux-aarch64.so.1 --library-path /network083/usr/lib/aarch64-linux-gnu /network083/usr/sbin/wpa_cli -p /data/local/tmp/wpa_ctrl -i wlan0 "$1"
)
while :; do
    IFS=' ' read -r uptime090 rest090 < /proc/uptime
    seconds090=${uptime090%%.*}
    [ "$seconds090" -ge 100 ] && break
    /system/bin/sleep 1
done
scene090=$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)
case "$scene090" in
    ''|*[!0-9]*) printf 'REFRESH090_REFUSED reason=not_one_scene no_cycle=1\n'; exit 1 ;;
esac
/system/bin/sleep 10
current090=$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)
if [ "$current090" != "$scene090" ]; then
    printf 'REFRESH090_REFUSED reason=scene_changed no_cycle=1\n'
    exit 1
fi
guide090=$(/system/bin/pidof com.huawei.hmos.hwstartupguide 2>/dev/null || :)
if [ -z "$guide090" ] || [ ! -S /data/local/tmp/wpa_ctrl/wlan0 ]; then
    printf 'REFRESH090_REFUSED reason=guide_or_socket_absent no_cycle=1\n'
    exit 1
fi
printf 'REFRESH090_READY scene_pid=%s guide_pids=%s stable_interval=10\n' "$scene090" "$guide090"
printf 'REFRESH090_STATUS_BEFORE_BEGIN\n'
cli090 status > /data/refresh090-before.status 2>&1
status090=$?
/system/bin/cat /data/refresh090-before.status
printf 'REFRESH090_STATUS_BEFORE_END exit_status=%s\n' "$status090"
if [ "$status090" -ne 0 ] || ! /system/bin/grep -F -x -q 'wpa_state=COMPLETED' /data/refresh090-before.status; then
    printf 'REFRESH090_REFUSED reason=association_not_completed no_cycle=1\n'
    exit 1
fi
printf 'REFRESH090_DISCONNECT_BEGIN\n'
/system/bin/cat /proc/uptime
cli090 disconnect
printf 'REFRESH090_DISCONNECT_RESULT exit_status=%s response_not_inferred=1\n' "$?"
/system/bin/sleep 3
printf 'REFRESH090_STATUS_DISCONNECTED_BEGIN\n'
cli090 status
printf 'REFRESH090_STATUS_DISCONNECTED_END exit_status=%s\n' "$?"
printf 'REFRESH090_RECONNECT_BEGIN restore_even_if_disconnect_failed=1\n'
cli090 reconnect
printf 'REFRESH090_RECONNECT_RESULT exit_status=%s response_not_inferred=1\n' "$?"
for target090 in 120 135; do
    while :; do
        IFS=' ' read -r uptime090 rest090 < /proc/uptime
        seconds090=${uptime090%%.*}
        [ "$seconds090" -ge "$target090" ] && break
        /system/bin/sleep 1
    done
    printf 'REFRESH090_SAMPLE target=%s\n' "$target090"
    /system/bin/cat /proc/uptime
    printf 'REFRESH090_SCENE_PIDS '
    /system/bin/pidof com.ohos.sceneboard || :
    printf '\nREFRESH090_GUIDE_PIDS '
    /system/bin/pidof com.huawei.hmos.hwstartupguide || :
    printf '\nREFRESH090_STATUS_AFTER_BEGIN target=%s\n' "$target090"
    cli090 status
    printf 'REFRESH090_STATUS_AFTER_END target=%s exit_status=%s\n' "$target090" "$?"
done
printf 'REFRESH090_END desktop_not_inferred=1 original_callbacks_required=1\n'
