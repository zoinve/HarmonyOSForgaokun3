"""Read-only evidence verification; stage timings are not measured display FPS."""
from pathlib import Path
import runpy,json,re,statistics,math,hashlib
base=Path(__file__).resolve().parent
common=runpy.run_path(str(base/'verify-native-original-graphics-runtime-004.py'))['verify']
pixels=runpy.run_path(str(base/'extract-native-scanout-013.py'))['extract']
def verify(number):
    root=base.parent/f'reports/native-original-graphics-boot-{number:03}'
    result=common(root,data_bytes=3221225472)
    runtime=json.loads((root/'runtime-result.json').read_text())
    text=(root/'native-logs'/runtime['logs'][-1]['name']).read_bytes().decode(errors='replace')
    assert result['init_root_stable_verified'] and result['target_selinux_permissive_samples']==12
    assert 'renderer=FD690 vendor=freedreno version=OpenGL ES 3.2 Mesa 25.0.1' in text
    assert 'logical=2560x1600 panel=1600x2560 rotation=CW' in text
    assert 'screenWidth[2560] screenHeight[1600]' in text
    # Actual kernel accounting, not merely a mapped graphics library.
    gpu=[int(v) for v in re.findall(r'drm-engine-gpu:\s*(\d+) ns',text)]
    assert gpu and max(gpu)>min(v for v in gpu if v>0)>0
    assert 'usual.event.SCREEN_UNLOCKED' in text
    records=set(re.findall(r'NATIVE_PERF023 pid=(\d+) uid=(\d+) stage=([^ ]+) mono_us=(\d+) elapsed_us=(\d+)[^\n]*',text))
    stages={}
    for stage in ('egl_readback_finish','egl_copy_frame','composer_copy_rotate','composer_wait_flip'):
        rows=[r for r in records if r[2]==stage]
        assert len(rows)>20
        assert all(int(r[1])==(3036 if stage.startswith('composer_') else 1003) for r in rows)
        values=sorted(int(r[4]) for r in rows)
        stages[stage]=dict(samples=len(values),min_us=min(values),median_us=statistics.median(values),p95_us=values[math.ceil(len(values)*.95)-1],max_us=max(values))
    extracted=pixels(text)
    assert [n for n,raw in extracted]==[9,11]
    images=[]
    for sample,raw in extracted:
        path=root/f'scanout-sample-{sample}.ppm'
        assert path.read_bytes()==raw
        images.append(dict(sample=sample,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    assert runtime['screen_off_timer']=='active' and runtime['ubuntu_lsm']=='capability,landlock'
    assert 'OneShot Entry:' not in runtime['boot_status']
    assert 'ro,' in runtime['lab_mount'] and 'norecovery' in runtime['lab_mount']
    for row in runtime['logs']:
        t=(root/'native-logs'/row['name']).read_bytes().decode(errors='replace')
        assert not re.search(r'exit with signal : (6|11)\b',t)
    result.update(logical_size=[2560,1600],actual_panel_size=[1600,2560],actual_gpu_renderer='FD690 / Freedreno / Mesa 25.0.1',hardware_gpu_execution_verified=True,gpu_engine_time_values_ns=gpu,
        stage_timings=stages,scanout_images=images,frame_rate_measured=False,human_touch_orientation_verified=False,animation_smoothness_verified=False)
    return result
if __name__=='__main__':
    results={str(n):verify(n) for n in (23,24)}
    before=results['23']['stage_timings']['composer_copy_rotate']['median_us']
    after=results['24']['stage_timings']['composer_copy_rotate']['median_us']
    assert after<before
    summary=dict(trials=results,copy_rotation_median_speedup=before/after,copy_rotation_median_reduction_percent=(1-after/before)*100,
                 actual_fps_or_60_120hz_smoothness_claimed=False,remaining_bottleneck='synchronous GPU readback plus CPU presentation copies')
    with (base.parent/'reports/native-landscape-performance-023-024-verification.json').open('x') as f:json.dump(summary,f,indent=2)
    print(json.dumps(dict(copy_rotation_before_us=before,copy_rotation_after_us=after,speedup=before/after,verified_snapshots=sum(len(json.loads((base.parent/f'reports/native-original-graphics-boot-{n:03}/runtime-result.json').read_text())['logs']) for n in (23,24)),actual_fps_measured=False),indent=2))
