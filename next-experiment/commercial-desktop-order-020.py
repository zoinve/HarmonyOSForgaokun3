"""Follow the existing reference's normal aa path, without fabricating account state."""
def repair(original):
    wait='''checks=0
while [ "$checks" -lt 30 ]; do
    [ "$(read_param bootevent.account.ready)" = true ] && break
    checks=$((checks + 1))
    /system/bin/sleep 1
done
'''
    gate='if [ "$(read_param bootevent.account.ready)" = true ] && \\\n'
    assert original.count(wait)==1 and original.count(gate)==1
    prefix=original[:original.index(gate)].replace(wait,'# SceneBoard must exist before the normal account activation callback can finish.\n',1)
    old=original[original.index(gate):]
    assert '-b com.ohos.sceneboard' in old and '-a com.ohos.sceneboard.MainAbility' in old and '-m pc_sceneboard' in old
    return prefix+'''# Reference: HarmonyMac ports/tests/native-desktop-start.sh, normal Ability Manager entry.
# User 100 is the real STANDARD account created by the original Account Manager.
# Selecting it through aa does not activate it or bypass any authorization.
if [ "$(read_param bootevent.appfwk.ready)" = true ] && \\
   [ "$(read_param bootevent.bms.main.bundles.ready)" = true ]; then
    if /system/bin/pidof com.ohos.sceneboard >/dev/null 2>&1; then
        exit 0
    fi
    printf '<6>COMMERCIAL020_SCENEBOARD_START user_id=100 normal_aa=1\n' > /dev/kmsg
    /usr/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard -u 100 > /dev/kmsg 2>&1
    result=$?
    printf '<6>COMMERCIAL020_SCENEBOARD_RESULT result=%s user_id=100\n' "$result" > /dev/kmsg
    exit "$result"
fi
'''
