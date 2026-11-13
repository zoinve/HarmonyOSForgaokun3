"""Deduplicate cumulative snapshots; compare measured stages, never infer FPS."""
from pathlib import Path
import collections,json,re,statistics
root=Path(__file__).resolve().parent.parent/'reports'
pattern=re.compile(r'NATIVE_PERF023 pid=(\d+) uid=(\d+) stage=(\S+) mono_us=(\d+) elapsed_us=(\d+)')
def stages(directory):
    raw=directory/'runtime-evidence/raw'
    latest=max(raw.glob('phase-*.log'),key=lambda p:int(p.stem.split('-')[1]))
    text=latest.read_text(errors='replace')
    unique=set(pattern.findall(text))
    groups=collections.defaultdict(list)
    for pid,uid,stage,mono,elapsed in unique:groups[stage].append(int(elapsed))
    out={}
    for stage,values in groups.items():
        values.sort()
        out[stage]=dict(samples=len(values),mean_us=round(statistics.mean(values),2),median_us=statistics.median(values),
            min_us=min(values),max_us=max(values),p90_us=values[min(len(values)-1,int(len(values)*.9))])
    return dict(snapshot=latest.name,raw_records=len(pattern.findall(text)),unique_records=len(unique),stages=out,
        target_timeout='target_timeout=1' in text,target_end='NATIVE_ORIGINAL_END' in text,
        active_fd690_gl='stage=active_gl_context' in text and 'renderer=FD690 vendor=freedreno' in text,desktop_fps_verified=False)
if __name__=='__main__':
    before=stages(root/'native-original-graphics-boot-033')
    after=stages(root/'native-original-graphics-boot-034')
    stage='composer_copy_rotate'
    r=dict(baseline033=before,accelerated034=after,
        copy_rotate_mean_speedup=round(before['stages'][stage]['mean_us']/after['stages'][stage]['mean_us'],3),
        same_idle_workload_not_interactive_benchmark=True,physical_cursor_tested=False,gpu_rotation=False,stable_120fps_achieved=False)
    with (root/'native-original-graphics-boot-034/runtime-performance-comparison.json').open('x') as f:json.dump(r,f,indent=2)
    print(json.dumps(r,indent=2))
