#!/system/bin/sh
set -u
umask 077
set -C
exec > /data/commercial-memmgr-stack109.log 2>&1 || exit 1
printf 'MEMSTACK109_BEGIN original_service_only=1 state_unmodified=1\n'
hash109=$(/system/bin/sha256sum /reference-stack-probe103 2>/dev/null || :)
[ "$hash109" = 'bc9f14107ebfb682311bf8c714f148df579141bb443a358ff85199cdc443b181  /reference-stack-probe103' ] || {
    printf 'MEMSTACK109_REFUSED reason=probe_hash\n'; exit 1;
}
pid109=''
for attempt109 in $(/system/bin/seq 1 400); do
    pid109=$(/system/bin/pidof memmgrservice 2>/dev/null || :)
    [ -n "$pid109" ] && break
    /system/bin/sleep 0.1
done
case "$pid109" in
    ''|*[!0-9]*|0|1) printf 'MEMSTACK109_REFUSED reason=target_not_unique\n'; exit 1 ;;
esac
for phase109 in first later; do
    current109=$(/system/bin/pidof memmgrservice 2>/dev/null || :)
    [ "$current109" = "$pid109" ] || { printf 'MEMSTACK109_REFUSED reason=target_changed\n'; exit 1; }
    printf 'MEMSTACK109_DFX_BEGIN phase=%s pid=%s\n' "$phase109" "$pid109"
    /system/bin/cat /proc/uptime
    /system/bin/timeout 12 /reference-stack-probe103 "$pid109" all
    status109=$?
    printf 'MEMSTACK109_DFX_END phase=%s status=%s success_not_inferred=1\n' "$phase109" "$status109"
    /system/bin/cat /proc/uptime
    printf 'MEMSTACK109_NAMESPACE_BEGIN phase=%s\n' "$phase109"
    /system/bin/cat "/proc/$pid109/mountinfo"
    /system/bin/ls -ldn "/proc/$pid109/root/dev/memcg"
    /system/bin/ls -ln "/proc/$pid109/root/dev/memcg/"
    printf 'MEMSTACK109_NAMESPACE_END phase=%s\n' "$phase109"
    [ "$phase109" = first ] && /system/bin/sleep 20
done
printf 'MEMSTACK109_END desktop_not_inferred=1\n'
