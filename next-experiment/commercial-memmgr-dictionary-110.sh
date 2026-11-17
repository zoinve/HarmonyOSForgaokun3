#!/system/bin/sh
set -u
umask 077
set -C
exec > /data/commercial-memmgr-dictionary110.log 2>&1 || exit 1
printf 'DICT110_BEGIN original_generator=1 original_checks_retained=1\n'
cli110=$(/system/bin/sha256sum /system/bin/hilog 2>/dev/null || :)
elf110=$(/system/bin/sha256sum /system/lib64/libmemmgrservice.z.so 2>/dev/null || :)
[ "$cli110" = '9dbdb63bcec42fba4c8a629207b9dab0914fb60b8e669e0ab65b84915cf7d04e  /system/bin/hilog' ] || {
    printf 'DICT110_REFUSED reason=cli_hash\n'; exit 1;
}
[ "$elf110" = '2cf2566bb7bf580513e82c6d1819775886cfe3ecd35a5e2b14a0eae60dceb012  /system/lib64/libmemmgrservice.z.so' ] || {
    printf 'DICT110_REFUSED reason=service_elf_hash\n'; exit 1;
}
for poll110 in $(/system/bin/seq 1 400); do
    daemon110=$(/system/bin/pidof hilogd 2>/dev/null || :)
    [ -n "$daemon110" ] && break
    /system/bin/sleep 0.1
done
case "$daemon110" in
    ''|*[!0-9]*|0|1) printf 'DICT110_REFUSED reason=daemon_not_unique\n'; exit 1 ;;
esac
printf 'DICT110_GENERATOR_BEGIN\n'
/system/bin/cat /proc/uptime
/system/bin/timeout 15 /system/bin/hilog -d /system/lib64/libmemmgrservice.z.so
status110=$?
printf 'DICT110_GENERATOR_END status=%s success_not_inferred=1\n' "$status110"
/system/bin/cat /proc/uptime
dict110=/data/log/dict/DA/6DFBB4628DCEB0F153CA268C4747DF
if [ -f "$dict110" ] && [ ! -L "$dict110" ]; then
    printf 'DICT110_EXPECTED_FILE_PRESENT value=1\n'
    /system/bin/ls -ln "$dict110"
    /system/bin/sha256sum "$dict110"
else
    printf 'DICT110_EXPECTED_FILE_PRESENT value=0\n'
fi
for poll110 in $(/system/bin/seq 1 400); do
    pid110=$(/system/bin/pidof memmgrservice 2>/dev/null || :)
    [ -n "$pid110" ] && break
    /system/bin/sleep 0.1
done
case "$pid110" in
    ''|*[!0-9]*|0|1) printf 'DICT110_REFUSED reason=service_not_unique\n'; exit 1 ;;
esac
for phase110 in first later; do
    current110=$(/system/bin/pidof memmgrservice 2>/dev/null || :)
    [ "$current110" = "$pid110" ] || { printf 'DICT110_REFUSED reason=service_changed\n'; exit 1; }
    printf 'DICT110_QUERY_BEGIN phase=%s pid=%s\n' "$phase110" "$pid110"
    /system/bin/cat /proc/uptime
    /system/bin/timeout 6 /system/bin/hilog -x -P "$pid110"
    status110=$?
    printf 'DICT110_QUERY_END phase=%s status=%s decoded_messages_not_inferred=1\n' "$phase110" "$status110"
    [ "$phase110" = first ] && /system/bin/sleep 20
done
printf 'DICT110_END desktop_not_inferred=1\n'
