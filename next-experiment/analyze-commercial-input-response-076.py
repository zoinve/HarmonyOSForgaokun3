"""Correlate real keyboard timing with the original public input-framework log."""
from pathlib import Path
import hashlib
import json
import re
import sys

number = sys.argv[1] if len(sys.argv) == 2 else '076'
assert number in ['075', '076']
root = Path(__file__).resolve().parents[1] / ('reports/commercial61-native-' + number)
raw = root / 'runtime-evidence/raw'
manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
for name, item in manifest['files'].items():
    data = (raw / name).read_bytes()
    assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
phase = max(raw.glob('phase-*.log'), key=lambda p:int(p.stem.split('-')[1])).read_text(errors='replace')
writer = re.findall(r'COMMERCIAL' + number + r'_KEYBOARD key=LEFTMETA path=([^ ]+) down_bytes=(\d+) up_bytes=(\d+) expected_bytes=(\d+) response_not_inferred=1', phase)
hilog = (raw / 'interactive-hilog030.log').read_text(errors='replace').splitlines()
events = []
for index,line in enumerate(hilog,1):
    if '/multimodalinput/EventNormalizeHandler:' not in line or 'HandleKeyboardEvent:477' not in line:
        continue
    match = re.search(r'\[K:([DU]):(\d+)\].*AT:(\d+),.*KA:KEY_ACTION_(DOWN|UP)',line)
    if not match or not 132000000 <= int(match[3]) < 133500000:
        continue
    ident = match[2]
    nearby = hilog[max(index-4,0):index+5]
    physical = any('InputTracking id:' + ident in row and 'event created by:HID 12d1:10b8 Keyboard' in row for row in nearby)
    device = next((re.search(r'DN:(\d+)',row)[1] for row in nearby
                   if '[K:' + match[1] + ':' + ident + ']' in row and re.search(r'DN:(\d+)',row)),None)
    events.append(dict(line=index,id=int(ident),action=match[4],mono_us=int(match[3]),device=device,
                       physical_keyboard=physical,text=line))
pairs = [(down,up) for down in events for up in events
         if down['action']=='DOWN' and up['action']=='UP' and down['physical_keyboard'] and up['physical_keyboard']
         and down['device']==up['device']=='6' and 70000<=up['mono_us']-down['mono_us']<=100000]
scene = [dict(line=i,text=line) for i,line in enumerate(hilog,1)
         if re.match(r'01-01 08:02:1[23]\.',line) and '/com.ohos.sceneboard/HOME:' in line
         and ('PreLogoKeyEvent' in line or 'LogoKey' in line)]
receivers = [dict(line=i,text=line) for i,line in enumerate(hilog,1)
             if any('[K:' + ('D' if event['action']=='DOWN' else 'U') + ':' + str(event['id']) + ']' in line for event in events)
             and '/InputManagerImpl:' in line]
writer_ok = bool(writer) and all(int(down)==int(up)==int(expected)>0 for _,down,up,expected in writer)
result = dict(run=manifest['run'], verified_files=len(manifest['files']), writer_records=writer,
    kernel_write_lengths_complete=writer_ok, input_events=events,
    matching_80ms_physical_keyboard_pairs=[dict(down=d,up=u) for d,u in pairs],
    public_application_receivers=receivers, scene_logo_processing=scene,
    framework_keyboard_delivery_verified=writer_ok and bool(pairs) and bool(scene),
    other_user_input_may_also_be_present=True, screenshot_change_not_automatically_causal=True,
    keycode_privacy_redaction_preserved=True, desktop_verified=False, interaction_verified=False)
(root / 'input-response-analysis.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(dict(run=result['run'], writer_records=writer, matched_pairs=len(pairs),
    scene_logo_processing=scene, framework_keyboard_delivery_verified=result['framework_keyboard_delivery_verified'],
    interaction_verified=False),indent=2))
