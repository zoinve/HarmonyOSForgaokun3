"""Retry genuine account activation after the original SceneBoard is ready."""
from pathlib import Path
import runpy


def repair(original):
    baseline = runpy.run_path(str(Path(__file__).with_name('commercial-desktop-order-021.py')))['repair'](original)
    retry = runpy.run_path(str(Path(__file__).with_name('commercial-desktop-retry-032.py')))
    baseline = retry['repair'](baseline)
    prefix, launch = baseline.split(retry['ANCHOR'])
    # Scope the existing launch exits to a subshell; preserve all BMS retries.
    return prefix + retry['ANCHOR'] + '\n(\n' + launch + '''
)
launch_result=$?
[ "$launch_result" -eq 0 ] || exit "$launch_result"
# Retry only after genuine SceneBoard/WMS readiness, never set boot flags here.
checks=0
while [ "$checks" -lt 90 ]; do
    if /system/bin/pidof com.ohos.sceneboard >/dev/null 2>&1 &&
       [ "$(read_param bootevent.wms.ready)" = true ]; then
        break
    fi
    checks=$((checks + 1))
    /system/bin/sleep 1
done
[ "$(read_param bootevent.wms.ready)" = true ] || exit 1
/system/bin/pidof com.ohos.sceneboard >/dev/null 2>&1 || exit 1
if [ "$(read_param bootevent.account.ready)" != true ]; then
    printf '<6>COMMERCIAL062_ACCOUNT_RETRY original_acm=1 local_id=100\n' > /dev/kmsg
    /system/bin/acm switch -i 100 > /dev/kmsg 2>&1
    result=$?
    printf '<6>COMMERCIAL062_ACCOUNT_RESULT result=%s\n' "$result" > /dev/kmsg
    exit "$result"
fi
'''
