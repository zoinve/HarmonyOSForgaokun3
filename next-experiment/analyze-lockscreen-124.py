"""Correlate original lockscreen logs with lossless frame OCR, not visual claims."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
folder=BASE.parent/'reports/commercial61-native-124'
output=folder/'lockscreen-late-analysis.json'
assert not output.exists()
manifest=json.loads((folder/'runtime-evidence/retrieval-manifest.json').read_text())
raw=(folder/'runtime-evidence/raw/interactive-hilog030.log').read_bytes()
assert hashlib.sha256(raw).hexdigest()==manifest['files']['interactive-hilog030.log']['sha256']
sanitize=runpy.run_path(str(BASE/'analyze-original-devicedetect-095.py'))['sanitize']
patterns={
    'lock_state':rb'(?:isScreenLocked|IsScreenLocked|isLocked|screenLockState|ScreenLockState|SetScreenLock|setScreenLock|isScreenLock)',
    'lock_lifecycle':rb'(?:screenlock|ScreenLock|LockScreen|lockscreen).*(?:onCreate|onForeground|onBackground|onWindowStage|unlock|Unlock|locked|Locked|show|Show|hide|Hide|ready|Ready)',
    'unlock':rb'(?:unlock|Unlock).*(?:fail|Fail|success|Success|password|Password|credential|Credential|request|Request)',
}
evidence={key:[] for key in patterns}
counts={key:0 for key in patterns}
for number,line in enumerate(raw.splitlines(),1):
    if len(line)>=4096:continue
    for key,pattern in patterns.items():
        if re.search(pattern,line):
            counts[key]+=1
            evidence[key].append(dict(line=number,text=sanitize(line)))
            if len(evidence[key])>100:
                evidence[key].pop(0)
ocr=subprocess.run(['tesseract',str(folder/'full-frame/source.png'),'stdout','-l','eng'],capture_output=True,text=True,check=True)
result=dict(run=manifest['run'],source_hilog_sha256=manifest['files']['interactive-hilog030.log']['sha256'],
    counts=counts,evidence=evidence,frame_ocr=ocr.stdout,
    ocr_is_not_visual_inspection=True,desktop_verified=False,interaction_verified=False,
    commercial_activation_modified=False)
output.open('x').write(json.dumps(result,indent=2))
print(json.dumps(dict(counts=counts,late_lifecycle=evidence['lock_lifecycle'][-12:],late_state=evidence['lock_state'][-6:]),indent=2))
