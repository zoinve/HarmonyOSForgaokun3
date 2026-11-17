"""Gate only the existing early Home launcher on an original service event."""
ANCHOR = '# Reference: HarmonyMac ports/tests/native-desktop-start.sh, normal Ability Manager entry.\n'
GATE = '''# Wait for the observed original collaboration initialization checkpoint.
# A timeout is a diagnostic failure, not permission to fabricate readiness.
/system/bin/timeout 95 /system/bin/sh /commercial-collaboration-ready116.sh
checkpoint_result116=$?
if [ "$checkpoint_result116" -ne 0 ]; then
    printf 'COMMERCIAL116_HOME_GATE_FAILED status=%s\\n' "$checkpoint_result116"
    exit "$checkpoint_result116"
fi
'''


def adapt(original):
    assert original.count(ANCHOR) == 1
    assert original.count('/usr/bin/aa start -b com.ohos.sceneboard') == 1
    return original.replace(ANCHOR, GATE + ANCHOR, 1)
