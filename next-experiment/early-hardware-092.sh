#!/bin/busybox sh
# The original core later binds this RAM file read-only before original init.
prepare_model092() {
    firmware=$1
    para=$2
    [ ! -L "$para" ] && [ -f "$para" ] || return 10
    [ "$(/bin/busybox sha256sum "$para")" = "PARAM_SHA  $para" ] || return 11
    [ "$(/bin/busybox stat -f -c %t "$firmware")" = 62656572 ] || return 12
    board=$(/bin/busybox tr -d '\000' < "$firmware/firmware/devicetree/base/model") || return 13
    case "$board" in *'Matebook E Go'*) ;; *) return 13 ;; esac
    vendor=$(/bin/busybox cat "$firmware/class/dmi/id/sys_vendor") || return 14
    model=$(/bin/busybox cat "$firmware/class/dmi/id/product_name") || return 14
    [ ${#vendor} -gt 0 ] && [ ${#vendor} -lt 36 ] || return 15
    [ ${#model} -gt 0 ] && [ ${#model} -lt 36 ] || return 15
    case "$vendor:$model" in *[!A-Za-z0-9_:.-]*) return 15 ;; esac
    case "$model" in default|Default|unknown|Unknown|None|none|ohos|ToBeFilled*) return 15 ;; esac
    /bin/busybox awk -F= -v vendor="$vendor" '
        $1 == "const.product.manufacturer" { n++; if ($2 != vendor) bad=1 }
        $1 == "const.product.model" { m++ }
        END { exit !(n == 1 && m == 1 && !bad) }
    ' "$para" || return 16
    [ ! -e "$para.early092" ] && [ ! -L "$para.early092" ] || return 17
    (set -C; /bin/busybox awk -F= -v model="$model" '
        $1 == "const.product.model" { print "const.product.model=" model; next }
        { print }
    ' "$para" > "$para.early092") || return 18
    /bin/busybox chmod 0644 "$para.early092" || return 19
    /bin/busybox mv "$para.early092" "$para" || return 20
    printf 'EARLY092_MODEL supplied_from_real_sysfs=1 model_length=%s serial_read=0 original_init_unchanged=1\n' "${#model}"
}

if [ "$$" -ne 1 ] || [ "$(/bin/busybox id -u)" != 0 ]; then
    printf 'EARLY092_REFUSED requires_pid1_root\n' >&2
    exit 77
fi
if [ "$(/bin/busybox sha256sum /init)" != 'CORE_SHA  /init' ]; then
    printf 'EARLY092_REFUSED original_core_hash\n' >&2
    /bin/busybox reboot -f
    exit 78
fi
log=/native-target/hardware-early092.log
if (set -C; : > "$log"); then
    if /bin/busybox mount -n -t sysfs -o nosuid,nodev,noexec sysfs /early-sys092; then
        prepare_model092 /early-sys092 /native-target/graphics016/sys_prod/etc/param/hw_defaults.para >> "$log" 2>&1
        result=$?
        printf 'EARLY092_RESULT status=%s activation_success_not_inferred=1\n' "$result" >> "$log"
        /bin/busybox umount /early-sys092
        printf 'EARLY092_UNMOUNT status=%s\n' "$?" >> "$log"
    else
        printf 'EARLY092_REFUSED sysfs_mount no_parameter_write=1\n' >> "$log"
    fi
    /bin/busybox cat "$log"
fi
exec /init "$@"
