#!/system/bin/sh
/system/bin/sh /harmonymac-reference099.sh
result099=$?
exec >> /data/commercial-direct-desktop075.log 2>&1
printf 'REFERENCE099_RETURN status=%s desktop_not_inferred=1\n' "$result099"
for sample099 in 90 110 130 145; do
    while :; do
        IFS=' ' read -r uptime099 rest099 < /proc/uptime
        seconds099=${uptime099%%.*}
        [ "$seconds099" -ge "$sample099" ] && break
        /system/bin/sleep 1
    done
    printf 'REFERENCE099_SAMPLE target=%s\n' "$sample099"
    /system/bin/cat /proc/uptime
    printf 'REFERENCE099_SCENE_PIDS '
    /system/bin/pidof com.ohos.sceneboard || :
    printf '\nREFERENCE099_GUIDE_PIDS '
    /system/bin/pidof com.huawei.hmos.hwstartupguide || :
    printf '\n'
    /system/bin/timeout 3 /system/bin/hidumper -s 4606 -a -a
    printf 'REFERENCE099_SAMPLE_END target=%s\n' "$sample099"
done
