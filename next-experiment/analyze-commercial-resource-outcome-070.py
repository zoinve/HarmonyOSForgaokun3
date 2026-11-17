"""Compare original app messages; do not equate file visibility with success."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re

base=Path(__file__).resolve().parents[1]/'reports'


def observe(number):
    root=base/('commercial61-native-'+number)
    raw=root/'runtime-evidence/raw'
    manifest=json.loads((raw.parent/'retrieval-manifest.json').read_text())
    for name,item in manifest['files'].items():
        data=(raw/name).read_bytes()
        assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
    lines=(raw/'interactive-hilog030.log').read_text(errors='replace').splitlines()
    app=[line for line in lines if '/com.huawei.hmos.hwstartupguide/' in line]
    names=Counter()
    for line in app:
        match=re.search(r'Get rawFile error, filename:([^,]+), error:(\d+)',line)
        if match:
            names[match[1]+':'+match[2]]+=1
    return dict(run=manifest['run'],verified_files=len(manifest['files']),
        startupguide_log_lines=len(app),rawfile_errors=dict(names),
        realpath_errors=sum('FindRawFile path to realpath error' in line for line in app),
        source_failed=sum('Video media player set media source failed' in line for line in app),
        system_resource_add_failed=sum('AddResource failed, hapPath: /system/app/SystemResources/SystemResources.hap' in line for line in lines),
        video_messages=[line for line in app if any(s in line for s in ['AceVideo:',
            'Video media player set media source failed','Page:loopVideo error','FindRawFile path to realpath error','Get rawFile error'])],
        layout_markers=[line for path in [raw/'interactive-faults030.log',raw/'original-init030.log']
            if path.exists() for line in path.read_text(errors='replace').splitlines()
            if 'COMMERCIAL070_ORIGINAL_RAWFILES' in line])


result=dict(baseline=observe('069'),candidate=observe('070'),
    original_app_success_requires_runtime_evidence=True,desktop_verified=False,interaction_verified=False)
with (base/'commercial61-native-070/resource-outcome-analysis.json').open('x') as out:
    json.dump(result,out,indent=2)
print(json.dumps({name:{k:v for k,v in item.items() if k not in ['video_messages','layout_markers']}
    for name,item in result.items() if isinstance(item,dict)},indent=2))
