"""Remove only the redundant development-script SceneBoard start request."""
LAUNCH = '/system/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard'
GUARD = '''if ! pidof com.ohos.sceneboard >/dev/null; then
    echo OOBE114_MISSING_EXISTING_SCENEBOARD
    exit 1
fi
echo OOBE114_EXISTING_SCENEBOARD_NO_SECOND_START'''


def adapt(reference):
    assert reference.count(LAUNCH + '\n') == 1
    assert reference.count('/system/bin/aa force-stop com.huawei.hmos.hwstartupguide') == 1
    return reference.replace(LAUNCH, GUARD, 1)
