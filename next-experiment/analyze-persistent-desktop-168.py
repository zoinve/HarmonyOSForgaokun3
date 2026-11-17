"""Compare known original desktop process and install evidence, without user data."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
def summarize(report):
    evidence=report/'runtime-evidence'
    manifest=json.loads((evidence/'retrieval-manifest.json').read_text())
    for name,row in manifest['files'].items():
        data=(evidence/'raw'/name).read_bytes()
        assert hashlib.sha256(data).hexdigest()==row['sha256'] and len(data)==row['bytes']
    latest=max((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log',n)),key=lambda n:int(n[6:-4]))
    phase=(evidence/'raw'/latest).read_text(errors='replace')
    hilog=(evidence/'raw/interactive-hilog030.log').read_text(errors='replace')
    desktop=(evidence/'raw/snapshot075-commercial-direct-desktop075.log').read_text(errors='replace')
    trace=(evidence/'raw/snapshot075-native-perf-023.trace').read_text(errors='replace')
    processes=re.findall(r'^COMMERCIAL001_PROCESS sample=(\d+) pid=(\d+) cmd=com\.ohos\.sceneboard(?:\s|$)',phase,re.M)
    samples=[int(sample) for sample,pid in processes]
    frames=re.findall(r'^COMMERCIAL030_FRAME sequence=(\d+) mono_us=(\d+).*output_valid=1 output_nonblack=(\d+)',trace,re.M)
    result=dict(run=manifest['run'],sceneboard_process_samples=samples,
        sceneboard_present_at_late_sample=any(sample>=15 for sample in samples),
        original_sceneboard_install_results=[int(code) for code in re.findall(r'finish install com\.ohos\.sceneboard resultCode: (-?\d+)',hilog)],
        original_sceneboard_boot_install_scheduled=hilog.count('BootStartInstall : /system/app/SceneBoard'),
        existing_scene_guard_passed='OOBE114_EXISTING_SCENEBOARD_NO_SECOND_START' in desktop,
        existing_scene_guard_failed='OOBE114_MISSING_EXISTING_SCENEBOARD' in desktop,
        valid_nonblack_composer_frame_count=sum(int(nonblack)>0 for sequence,mono,nonblack in frames),
        latest_composer_frame_monotonic_us=max((int(mono) for sequence,mono,nonblack in frames),default=None),
        physical_desktop_interaction_verified=False)
    return result

if __name__=='__main__':
    assert sys.argv[1:] in [['168'],['169']]
    report=ROOT/('reports/commercial61-native-'+sys.argv[1])
    result=dict(first_persistent_boot=summarize(ROOT/'reports/commercial61-native-166-compile-fix-1'),
        current_persistent_boot=summarize(report))
    (report/'persistent-desktop-analysis.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
