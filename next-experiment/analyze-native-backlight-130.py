"""Correlate genuine original RenderService requests and sysfs write returns."""
from pathlib import Path
import hashlib
import json
import re
import runpy

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
if __name__=='__main__':
    folder=ROOT/'reports/commercial61-native-130'
    output=folder/'backlight-runtime-analysis.json'
    assert not output.exists()
    manifest=json.loads((folder/'runtime-evidence/retrieval-manifest.json').read_text())
    phase=max((name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log',name)),key=lambda name:int(name[6:-4]))
    names=[phase,'interactive-hilog030.log','snapshot075-commercial-desktop086.log']
    sanitize=runpy.run_path(str(BASE/'analyze-original-devicedetect-095.py'))['sanitize']
    verified={};records=[];sets=[];gets=[];permissions=[];requests=[];failures=[];ending=[]
    for name in names:
        raw=(folder/'runtime-evidence/raw'/name).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==manifest['files'][name]['sha256']
        assert len(raw)==manifest['files'][name]['bytes']
        verified[name]=manifest['files'][name]['sha256']
        for number,line in enumerate(raw.splitlines(),1):
            if len(line)>4096:continue
            if b'GAOKUN_BACKLIGHT' in line:
                record=dict(file=name,line=number,text=sanitize(line))
                records.append(record)
                if b'GAOKUN_BACKLIGHT130_PERMISSION ' in line:permissions.append(record)
                match=re.search(rb'GAOKUN_BACKLIGHT129_SET device=(\d+) status=(-?\d+) requested=(\d+)',line)
                if match:sets.append(dict(device=int(match[1]),status=int(match[2]),requested=int(match[3]),**record))
                match=re.search(rb'GAOKUN_BACKLIGHT129_GET device=(\d+) status=(-?\d+) level=(\d+)',line)
                if match:gets.append(dict(device=int(match[1]),status=int(match[2]),level=int(match[3]),**record))
            if b'SetScreenBacklight id:' in line:requests.append(dict(file=name,line=number,text=sanitize(line)))
            if re.search(rb'(?:SetDisplayBacklight|SetScreenBacklight).*(?:fail|error)',line,re.I):failures.append(dict(file=name,line=number,text=sanitize(line)))
            if re.search(rb'COMMERCIAL087_TARGET_EXIT|COMMERCIAL087 target_timeout|NATIVE_ORIGINAL_END|NATIVE_DIAGNOSTIC_END',line):ending.append(sanitize(line))
    result=dict(run=manifest['run'],verified_input_sha256=verified,permission_records=permissions,original_requests=requests,
        composer_sets=sets,composer_gets=gets,failures=failures,all_backlight_markers=records,
        original_service_sysfs_write_verified=bool(permissions and requests and any(row['device']==0 and row['status']==0 for row in sets)),
        any_composer_error=any(row['status']!=0 for row in sets+gets),physical_luminance_verified=False,
        slider_interaction_verified=False,power_management_verified=False,ending=ending,
        only_basic_backlight_driver_changed=True,commercial_activation_modified=False)
    output.open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
