"""Retry only ordinary Ability Manager requests across the observed BMS publication gap."""
ANCHOR='# Reference: HarmonyMac ports/tests/native-desktop-start.sh, normal Ability Manager entry.'
def repair(original):
    assert original.count(ANCHOR)==1 and 'COMMERCIAL032_SCENEBOARD_ATTEMPT' not in original
    prefix,tail=original.split(ANCHOR)
    command='/usr/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard'
    assert tail.count(command)==1 and 'user_selection=aa_default' in tail
    return prefix+ANCHOR+'''
# A bundle-scan parameter can precede actual BMS publication. Do not fabricate readiness.
# A process check is only a launch observation, not desktop acceptance.
attempt=0
while [ "$attempt" -lt 6 ]; do
    if /system/bin/pidof com.ohos.sceneboard >/dev/null 2>&1; then
        echo "COMMERCIAL032_SCENEBOARD_PROCESS observed=1 attempts=$attempt desktop_verified=0" > /dev/kmsg
        exit 0
    fi
    attempt=$((attempt + 1))
    if [ "$(read_param bootevent.appfwk.ready)" = true ] && \\
       [ "$(read_param bootevent.bms.main.bundles.ready)" = true ]; then
        echo "COMMERCIAL032_SCENEBOARD_ATTEMPT attempt=$attempt user_selection=aa_default" > /dev/kmsg
        '''+command+''' > /dev/kmsg 2>&1
        result=$?
        echo "COMMERCIAL032_SCENEBOARD_CLI result=$result attempt=$attempt accepted_not_inferred=1" > /dev/kmsg
    fi
    /system/bin/sleep 2
done
if /system/bin/pidof com.ohos.sceneboard >/dev/null 2>&1; then
    echo "COMMERCIAL032_SCENEBOARD_PROCESS observed=1 attempts=$attempt desktop_verified=0" > /dev/kmsg
    exit 0
fi
echo "COMMERCIAL032_SCENEBOARD_PROCESS observed=0 attempts=$attempt" > /dev/kmsg
exit 1
'''
