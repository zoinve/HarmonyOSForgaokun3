#!/system/bin/sh
set -u
umask 077
set -C
exec > /data/commercial-desktop086.log 2>&1 || exit 1
printf 'CONFIG088_BEGIN inherited_log_name=086 no_input_injected=1 original_service_permissions_unchanged=1\n'
/system/bin/id
/system/bin/cat /proc/self/attr/current
printf 'CONFIG088_POLICY_PARAMETER_BEGIN\n'
/system/bin/timeout 4 /system/bin/param get const.cust.config_dir_layer
printf 'CONFIG088_POLICY_PARAMETER_END status=%s\n' "$?"
for target088 in 60 100 130; do
    while :; do
        IFS=' ' read -r uptime088 rest088 < /proc/uptime
        seconds088=${uptime088%%.*}
        [ "$seconds088" -ge "$target088" ] && break
        /system/bin/sleep 1
    done
    printf 'CONFIG088_SAMPLE target=%s\n' "$target088"
    /system/bin/cat /proc/uptime
    candidates088=$(/system/bin/pidof com.ohos.sceneboard 2>/dev/null || :)
    seen088=0
    for pid088 in $candidates088; do
        case "$pid088" in ''|*[!0-9]*) continue ;; esac
        seen088=$((seen088 + 1))
        [ "$seen088" -le 4 ] || break
        printf 'CONFIG088_PROCESS_BEGIN pid=%s target=%s\n' "$pid088" "$target088"
        /system/bin/cat "/proc/$pid088/comm"
        /system/bin/readlink "/proc/$pid088/ns/mnt"
        /system/bin/readlink "/proc/$pid088/root"
        for path088 in /system/etc/hw_launcher_default_workspace.json /usr/system/etc/hw_launcher_default_workspace.json; do
            printf 'CONFIG088_PATH_BEGIN pid=%s path=%s\n' "$pid088" "$path088"
            /system/bin/timeout 3 /system/bin/ls -ld "/proc/$pid088/root$path088"
            printf 'CONFIG088_STAT_RESULT status=%s\n' "$?"
            /system/bin/timeout 3 /system/bin/sha256sum "/proc/$pid088/root$path088"
            printf 'CONFIG088_HASH_RESULT status=%s\n' "$?"
            printf 'CONFIG088_PATH_END pid=%s path=%s\n' "$pid088" "$path088"
        done
        /system/bin/cat "/proc/$pid088/comm"
        printf 'CONFIG088_PROCESS_END pid=%s\n' "$pid088"
    done
    if [ "$target088" -ge 100 ]; then
        printf 'LAYOUT086_ATTEMPT target=%s\n' "$target088"
        /system/bin/timeout 8 /system/bin/uitest dumpLayout -p "/data/native-layout086-$target088.json"
        printf 'LAYOUT086_RESULT target=%s exit_status=%s success_not_inferred=1\n' "$target088" "$?"
    fi
done
printf 'CONFIG088_END desktop_not_inferred=1\n'
