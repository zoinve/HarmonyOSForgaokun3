#!/system/bin/sh
set -u
umask 077
[ -f /data/commercial-memmgr108.log ] && [ ! -L /data/commercial-memmgr108.log ] || exit 1
exec >> /data/commercial-memmgr108.log 2>&1 || exit 1
printf 'MEMMGR108_OBSERVER_BEGIN original_service_only=1 no_start_stop_commands=1\n'
for target108 in 20 40 60 80 100 120 140; do
    while :; do
        read uptime108 rest108 < /proc/uptime
        [ "${uptime108%%.*}" -ge "$target108" ] && break
        /system/bin/sleep 1
    done
    printf 'MEMMGR108_SAMPLE_BEGIN target=%s\n' "$target108"
    /system/bin/cat /proc/uptime
    /system/bin/pidof memmgrservice || :
    for key108 in startup.service.ctl.memmgrservice.pid init.svc.memmgrservice; do
        printf 'MEMMGR108_PARAM key=%s\n' "$key108"
        /system/bin/param get "$key108" || :
    done
    /system/bin/timeout 4 /system/bin/aurora/samgr-service-probe 1909
    result108=$?
    printf 'MEMMGR108_SA_PROBE status=%s service_success_not_inferred=1\n' "$result108"
    /system/bin/ls -ldn /dev/memcg /data/local/tmp/memmgr-nohyperhold-v1/memcg
    printf 'MEMMGR108_SAMPLE_END target=%s\n' "$target108"
done
printf 'MEMMGR108_OBSERVER_END desktop_not_inferred=1\n'
