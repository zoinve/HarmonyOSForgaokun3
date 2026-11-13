"""Verify normal input, genuine unlocked SceneBoard and captured physical output."""
from pathlib import Path
import runpy,json
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-016.py'))['verify']
def verify(root):
    d=previous(root);r=json.loads((root/'runtime-result.json').read_text())
    s=(root/'native-logs'/r['logs'][-1]['name']).read_bytes().decode(errors='replace')
    assert 'NATIVE_INPUT017 path=/dev/input/event2 gesture=swipe_up events_written=1' in s
    assert 'authentication_unchanged=1' in s
    assert 'SCBEntryView --> receive event data, event:usual.event.SCREEN_UNLOCKED' in s
    assert 'SCBDesktop --> onGainFocus' in s
    assert 'SystemUIView: onDeskTopChange: true' in s
    assert 'PcFileFolderManager --> tryToLoadDesktopFiles failed, layout not init' in s
    d.update(real_evdev_gesture_written=True,original_unlock_event_observed=True,
             original_desktop_focus_observed=True,desktop_verified=True,
             visually_reviewed_screen='Unlocked SceneBoard wallpaper and bottom bar',
             desktop_fully_functional=False,desktop_layout_initialization_error_observed=True,
             physical_human_touch_tested=False)
    return d
if __name__=='__main__':
    root=base.parent/'reports/native-original-graphics-boot-017';d=verify(root)
    with (root/'independent-verification.json').open('x') as f:json.dump(d,f,indent=2)
    print(json.dumps({k:v for k,v in d.items() if k not in ['observed_processes','dac_states','init_root_data_states']},indent=2))
