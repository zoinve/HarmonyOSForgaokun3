#!/system/bin/sh
set -u
umask 077
set -C
exec > /data/commercial-collaboration-ready116.log 2>&1 || exit 1
printf 'CFWK116_BEGIN original_event_only=1 no_service_start_stop=1\n'
/system/bin/cat /proc/uptime
server116=''
for poll116 in $(/system/bin/seq 1 30); do
    server116=$(/system/bin/pidof CollaborationFwk 2>/dev/null || :)
    [ -n "$server116" ] && break
    /system/bin/sleep 1
done
case "$server116" in
    ''|*[!0-9]*|0|1) printf 'CFWK116_REFUSED reason=server_not_unique\n'; exit 1 ;;
esac
fifo116=/data/commercial-collaboration-ready116.fifo
/system/bin/mkfifo "$fifo116" || exit 1
reader116=''
cleanup116()
{
    if [ -n "$reader116" ]; then
        kill -KILL "$reader116" 2>/dev/null || :
        wait "$reader116" 2>/dev/null || :
        reader116=''
    fi
    /system/bin/rm -f "$fifo116"
}
trap cleanup116 0
trap 'exit 1' 1 2 15
/system/bin/hilog > "$fifo116" 2>/dev/null &
reader116=$!
pattern116="^[0-9]{2}-[0-9]{2} [0-9:.]+[[:space:]]+${server116}[[:space:]]+[0-9]+[[:space:]]+I[[:space:]]+C0461C/CollaborationFwk/Detect: .*OnAddSystemAbilityEvent# RegisterHichainProofExceptionStatusCallback, ret: 0$"
event116=$(/system/bin/timeout 60 /system/bin/grep -E -m 1 "$pattern116" "$fifo116")
status116=$?
cleanup116
trap - 0 1 2 15
if [ "$status116" -ne 0 ] || [ -z "$event116" ]; then
    printf 'CFWK116_REFUSED reason=original_checkpoint_missing status=%s\n' "$status116"
    exit 1
fi
current116=$(/system/bin/pidof CollaborationFwk 2>/dev/null || :)
if [ "$current116" != "$server116" ]; then
    printf 'CFWK116_REFUSED reason=server_changed\n'
    exit 1
fi
printf 'CFWK116_ORIGINAL_EVENT pid=%s text=%s\n' "$server116" "$event116"
/system/bin/cat /proc/uptime
printf 'CFWK116_CHECKPOINT_OBSERVED full_service_readiness_not_inferred=1 desktop_not_inferred=1\n'
