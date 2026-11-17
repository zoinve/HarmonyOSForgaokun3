#!/system/bin/sh
set -u
umask 077
set -C
printf 'NORMAL_CLOSE095_BEGIN normal_window_request_only=1 no_force_stop=1 provisioning_unchanged=1\n'
while :; do
    IFS=' ' read -r uptime095 rest095 < /proc/uptime
    seconds095=${uptime095%%.*}
    [ "$seconds095" -ge 125 ] && break
    /system/bin/sleep 1
done
if [ "$seconds095" -gt 128 ]; then
    printf 'NORMAL_CLOSE095_REFUSED deadline_expired=1\n'
    exit 1
fi
scene095=$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)
guide095=$(/system/bin/pidof com.huawei.hmos.hwstartupguide 2>/dev/null || :)
case "$scene095" in ''|*[!0-9]*) printf 'NORMAL_CLOSE095_REFUSED ambiguous_scene=1\n'; exit 1;; esac
case "$guide095" in ''|*[!0-9]*) printf 'NORMAL_CLOSE095_REFUSED ambiguous_guide=1\n'; exit 1;; esac
helper095=$(/system/bin/sha256sum /native-normal-close095)
focus095=$(/system/bin/sha256sum /commercial-focus095.awk)
if [ "$helper095" != 'HELPER_SHA  /native-normal-close095' ] ||
   [ "$focus095" != 'FOCUS_SHA  /commercial-focus095.awk' ]; then
    printf 'NORMAL_CLOSE095_REFUSED diagnostic_hash_mismatch=1\n'
    exit 1
fi
if ! /system/bin/timeout 2 /system/bin/hidumper -s 4606 -a -a > /data/normal-close095-before.wms 2>&1; then
    printf 'NORMAL_CLOSE095_REFUSED window_dump_failed=1\n'
    exit 1
fi
/system/bin/cat /data/normal-close095-before.wms
if ! /system/bin/awk -v "guide=$guide095" -f /commercial-focus095.awk /data/normal-close095-before.wms; then
    printf 'NORMAL_CLOSE095_REFUSED guide_not_unique_focused_window=1\n'
    exit 1
fi
if [ "$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)" != "$scene095" ] ||
   [ "$(/system/bin/pidof com.huawei.hmos.hwstartupguide 2>/dev/null || :)" != "$guide095" ]; then
    printf 'NORMAL_CLOSE095_REFUSED processes_changed=1\n'
    exit 1
fi
/system/bin/cat /proc/uptime
/native-normal-close095 --send-once
printf 'NORMAL_CLOSE095_RESULT exit_status=%s window_dismissal_not_inferred=1\n' "$?"
for target095 in 130 140; do
    while :; do
        IFS=' ' read -r uptime095 rest095 < /proc/uptime
        [ "${uptime095%%.*}" -ge "$target095" ] && break
        /system/bin/sleep 1
    done
    printf 'NORMAL_CLOSE095_OBSERVE target=%s\n' "$target095"
    /system/bin/cat /proc/uptime
    /system/bin/pidof com.ohos.sceneboard com.huawei.hmos.hwstartupguide || :
    /system/bin/timeout 2 /system/bin/hidumper -s 4606 -a -a
done
printf 'NORMAL_CLOSE095_END desktop_not_inferred=1\n'
