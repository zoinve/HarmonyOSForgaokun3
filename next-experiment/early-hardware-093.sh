#!/bin/busybox sh
# Supply physical boot inputs in RAM; original init owns identity calculation.
prepare_hardware093() {
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
    for field in product_serial chassis_serial; do
        [ -f "$firmware/class/dmi/id/$field" ] && [ ! -L "$firmware/class/dmi/id/$field" ] || return 21
    done
    serial=$(/bin/busybox cat "$firmware/class/dmi/id/product_serial") || return 21
    chassis=$(/bin/busybox cat "$firmware/class/dmi/id/chassis_serial") || return 21
    [ ${#serial} -eq 16 ] && [ "$serial" = "$chassis" ] || return 22
    case "$serial" in *[!A-Za-z0-9]*) return 22 ;; esac
    digest=$(printf '%s' "$serial" | /bin/busybox sha256sum) || return 23
    [ "${digest%% *}" = SERIAL_SHA ] || return 23
    /bin/busybox awk -F= -v vendor="$vendor" '
        $1 == "const.product.manufacturer" { n++; if ($2 != vendor) bad=1 }
        $1 == "const.product.model" { m++ }
        $1 == "ohos.boot.sn" || $1 == "const.product.udid" || $1 == "const.product.devUdid" { bad=1 }
        END { exit !(n == 1 && m == 1 && !bad) }
    ' "$para" || return 16
    [ ! -e "$para.early093" ] && [ ! -L "$para.early093" ] || return 17
    (umask 077; set -C
        { /bin/busybox awk -F= -v model="$model" '
              $1 == "const.product.model" { print "const.product.model=" model; next }
              { print }
          ' "$para" && printf 'ohos.boot.sn=%s\n' "$serial"
        } > "$para.early093"
    ) || return 18
    /bin/busybox chmod 0600 "$para.early093" || return 19
    /bin/busybox mv "$para.early093" "$para" || return 20
    unset serial chassis digest
    printf 'EARLY093_INPUTS real_sysfs=1 model_length=%s serial_length=16 raw_values_exported=0 original_init_owns_udid=1\n' "${#model}"
}

if [ "$$" -ne 1 ] || [ "$(/bin/busybox id -u)" != 0 ]; then
    printf 'EARLY093_REFUSED requires_pid1_root\n' >&2
    exit 77
fi
if [ "$(/bin/busybox sha256sum /init)" != 'CORE_SHA  /init' ]; then
    printf 'EARLY093_REFUSED original_core_hash\n' >&2
    /bin/busybox reboot -f
    exit 78
fi
log=/native-target/hardware-early093.log
if (set -C; : > "$log"); then
    if /bin/busybox mount -n -t sysfs -o nosuid,nodev,noexec sysfs /early-sys092; then
        prepare_hardware093 /early-sys092 /native-target/graphics016/sys_prod/etc/param/hw_defaults.para >> "$log" 2>&1
        result=$?
        unset serial chassis digest
        printf 'EARLY093_RESULT status=%s activation_success_not_inferred=1\n' "$result" >> "$log"
        /bin/busybox umount /early-sys092
        printf 'EARLY093_UNMOUNT status=%s\n' "$?" >> "$log"
    else
        printf 'EARLY093_REFUSED sysfs_mount no_parameter_write=1\n' >> "$log"
    fi
    /bin/busybox cat "$log"
fi
exec /init "$@"
