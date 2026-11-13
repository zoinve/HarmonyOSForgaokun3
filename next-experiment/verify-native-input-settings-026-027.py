"""Read-only integrity and bounded input checks. Never infer Settings opens."""
from pathlib import Path
import runpy,json,re,hashlib
base=Path(__file__).resolve().parent
common=runpy.run_path(str(base/'verify-native-original-graphics-runtime-004.py'))['verify']
def verify(number):
    root=base.parent/'reports'/f'native-original-graphics-boot-{number:03d}'
    result=common(root,data_bytes=3221225472)
    runtime=json.loads((root/'runtime-result.json').read_text())
    text=(root/'native-logs'/runtime['logs'][-1]['name']).read_bytes().decode(errors='replace')
    assert len(runtime['logs'])==59
    for module in ['phy_qcom_snps_femto_v2','phy_qcom_qmp_usb','hid_multitouch']:
        assert f'NATIVE_INPUT026 module={module} status=0' in text
    assert 'x=0:2559 y=0:1599 authentication_unchanged=1' in text
    assert 'Name="HID 12d1:10b8 Keyboard"' in text
    assert 'Name="HID 12d1:10b8 Touchpad"' in text
    orientation=json.loads((root/'touch-orientation-026.json').read_text())
    assert orientation['target_dtb_sha256']=='5f6b1fa73d8bffa1984710d52c0babc4df297cbb90d9f4d9a48a433a104fb016'
    assert len(orientation['changed_properties'])==2
    if number==26:
        assert 'NATIVE_SETTINGS026 original_aa_start requested=1' in text
        assert 'Caller has no resolvable parent/hap token and lacks background-start permission, REJECT.' in text
        assert 'failed to start ability. result: 22' in text
    else:
        assert 'original_aa_start' not in text
        assert re.search(r'NATIVE_SETTINGS027 keyboard_meta_i path=/dev/input/event6 down_bytes=72 up_bytes=72 auth_unchanged=1',text)
        for event in [2,6,9]:
            assert re.search(r'NATIVE_INPUT027_FD sample=11 pid=\d+ fd=\d+ target=/dev/input/event'+str(event)+r'\n',text)
        assert 'usual.event.SCREEN_UNLOCKED' in text
        assert re.search(r'08:00:50\.\d+.*com.ohos.sceneboard/InputKeyFlow: OnInputEvent:',text)
    result.update(snapshot_count=len(runtime['logs']),touch_logical_axes=[2560,1600],
        dt_only_two_touch_properties_changed=True,usb_keyboard_touchpad_enumerated=True,
        original_mmi_holds_keyboard_touchpad_fds=number==27,
        real_kernel_key_events_reached_original_sceneboard=number==27,
        physical_finger_alignment_verified=False,physical_key_touchpad_gesture_tested=False,
        settings_main_window_verified=False,settings_root_cause_established=False,
        diagnostic_aa_background_start_rejected=number==26,permissions_bypassed=False,
        stable_120fps_verified=False,all_three_user_issues_resolved=False)
    return result
if __name__=='__main__':
    results={str(n):verify(n) for n in [26,27]}
    output=base.parent/'reports/native-input-settings-026-027-verification.json'
    with output.open('x',encoding='utf-8') as f:json.dump(results,f,indent=2)
    print(json.dumps(results,indent=2))
