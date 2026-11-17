"""Retry the original account service lifecycle, without caller impersonation."""
from pathlib import Path
import runpy

LOG = '/data/commercial-account-order063.log'


def repair(original):
    script = runpy.run_path(str(Path(__file__).with_name('commercial-desktop-order-062.py')))['repair'](original)
    start = script.index('if [ "$(read_param bootevent.account.ready)" != true ]; then',
                         script.index('# Retry only after genuine SceneBoard/WMS readiness'))
    assert script[start:].count('/system/bin/acm switch -i 100') == 1
    script = script[:start] + '''if [ "$(read_param bootevent.account.ready)" != true ]; then
    printf 'COMMERCIAL063_ACCOUNT_SERVICE_RETRY original_init=1\n'
    /usr/bin/begetctl stop_service accountmgr
    result=$?
    printf 'COMMERCIAL063_ACCOUNT_STOP_RESULT result=%s\n' "$result"
    [ "$result" -eq 0 ] || exit "$result"
    /usr/bin/begetctl start_service accountmgr
    result=$?
    printf 'COMMERCIAL063_ACCOUNT_START_RESULT result=%s\n' "$result"
    [ "$result" -eq 0 ] || exit "$result"
fi
checks=0
while [ "$checks" -lt 60 ]; do
    ready="$(read_param bootevent.account.ready)"
    if [ "$ready" = true ]; then
        printf 'COMMERCIAL063_ACCOUNT_READY observed_value=%s\n' "$ready"
        exit 0
    fi
    checks=$((checks + 1))
    /system/bin/sleep 1
done
printf 'COMMERCIAL063_ACCOUNT_READY_TIMEOUT checks=%s\n' "$checks"
exit 1
'''
    assert script.count('set -u\n') == 1
    setup = ('set -u\n(umask 077; : > ' + LOG + ') || exit 1\n'
             'exec >> ' + LOG + ' 2>&1\n'
             "printf 'COMMERCIAL063_ACCOUNT_SCRIPT_BEGIN\\n'\n")
    script = script.replace('set -u\n', setup, 1)
    return script.replace(' > /dev/kmsg', '')


def instrument_outer(outer):
    anchor = '    char path[256],expected[128]={},actual[128]={},text[4096];\n'
    assert outer.count(anchor) == 1
    extra = ('    snprintf(path,sizeof(path),"/proc/%d/root' + LOG + '",child);\n'
             '    commercial_outer_stream044(path,16384);\n')
    return outer.replace(anchor, anchor + extra, 1)
