"""Measure captured original-service GPU work; never substitute probe results."""
from pathlib import Path
import runpy,json,re
base=Path(__file__).resolve().parent
stages=runpy.run_path(str(base/'analyze-native-render-034.py'))['stages']
root=base.parent/'reports'
if __name__=='__main__':
    report=root/'native-original-graphics-boot-041'
    current=stages(report)
    raw=report/'runtime-evidence/raw'
    latest=raw/current['snapshot']
    text=latest.read_text(errors='replace')
    evidence=sorted(set(line for line in text.splitlines() if any(k in line for k in [
        'NATIVE_GPU041','call=gpu_scanout_','stage=composer_gpu_'])))
    ready=bool(re.search(r'NATIVE_COMPOSER007 pid=\d+ uid=3036 call=gpu_scanout_ready041 value=1',text))
    actual_gpu=current['stages'].get('composer_gpu_two_pass041',{}).get('samples',0)>0
    fallback=current['stages'].get('composer_gpu_cpu_fallback041',{}).get('samples',0)
    result=dict(original_service041=current,baseline034=stages(root/'native-original-graphics-boot-034'),
        original_composer_uid3036_gpu_scanout_ready=ready,gpu_frame_records_observed=actual_gpu,
        observed_gpu_frame_cpu_fallback_records=fallback,
        original_service_gpu_path_verified=ready and actual_gpu,
        evidence=evidence,timing_capture_is_bounded=True,physical_cursor_tested=False,
        interactive_workload_tested=False,statusbar_fixed=False,stable_120fps_achieved=False)
    with (report/'gpu-runtime-analysis.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
