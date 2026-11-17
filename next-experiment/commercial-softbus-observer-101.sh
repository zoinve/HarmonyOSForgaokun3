#!/system/bin/sh
exec >> /data/commercial-desktop086.log 2>&1
printf 'SOFTBUS101_OBSERVER_BEGIN readonly=1 no_service_restart=1\n'
for sample101 in 20 45 90 120 145; do
    while :; do
        IFS=' ' read -r uptime101 rest101 < /proc/uptime
        [ "${uptime101%%.*}" -ge "$sample101" ] && break
        /system/bin/sleep 1
    done
    printf 'SOFTBUS101_SAMPLE target=%s\n' "$sample101"
    /system/bin/cat /proc/uptime
    digest101=$(/system/bin/sha256sum /system/etc/init/softbus_server_musl.cfg)
    case "$digest101" in
        'CONFIG_SHA  /system/etc/init/softbus_server_musl.cfg') printf 'SOFTBUS101_CONFIG expected=1\n' ;;
        *) printf 'SOFTBUS101_CONFIG expected=0\n' ;;
    esac
    pids101=$(/system/bin/pidof softbus_server 2>/dev/null || :)
    printf 'SOFTBUS101_PIDS values=%s\n' "$pids101"
    for pid101 in $pids101; do
        case "$pid101" in ''|*[!0-9]*) continue ;; esac
        if [ -r "/proc/$pid101/maps" ]; then
            if /system/bin/grep -F -q '/system/lib64/l410-collaboration/libsoftbus_ble_pc_rsp_preload_v1.so' "/proc/$pid101/maps"; then
                printf 'SOFTBUS101_MAPPING pid=%s readable=1 platform_preload_present=1\n' "$pid101"
            else
                result101=$?
                if [ "$result101" -eq 1 ]; then
                    printf 'SOFTBUS101_MAPPING pid=%s readable=1 platform_preload_present=0\n' "$pid101"
                else
                    printf 'SOFTBUS101_MAPPING pid=%s readable=0 platform_preload_present=unknown\n' "$pid101"
                fi
            fi
        else
            printf 'SOFTBUS101_MAPPING pid=%s readable=0 platform_preload_present=unknown\n' "$pid101"
        fi
    done
    printf 'SOFTBUS101_SAMPLE_END target=%s\n' "$sample101"
done
printf 'SOFTBUS101_OBSERVER_END desktop_not_inferred=1\n'
