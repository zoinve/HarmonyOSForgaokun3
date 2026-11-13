"""Verify real SceneBoard and scanout; distinguish lock screen from desktop."""
from pathlib import Path
import runpy,json,re,hashlib
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-004.py'))['verify']
def verify(root):
    d=previous(root,data_bytes=3221225472);r=json.loads((root/'runtime-result.json').read_text())
    s=(root/'native-logs'/r['logs'][-1]['name']).read_bytes().decode(errors='replace')
    assert 'NATIVE_RAM_DATA016 bytes=3153108992' in s
    assert 'index=3 readonly=0 bytes=3221225472 ram_data=1' in s
    assert 'Publish SA:511 result:0' in s
    assert 'cmd=com.ohos.sceneboard ' in s
    assert 'com.ohos.sceneboard.MainAbility' in s
    extracts=runpy.run_path(str(base/'extract-native-scanout-013.py'))['extract'](s)
    assert len(extracts)==2
    for sample,raw in extracts:
        assert (root/f'scanout-sample-{sample}.ppm').read_bytes()==raw
        header=re.match(rb'P6\n160 256\n255\n',raw);assert header
        assert len(set(raw[header.end():]))>100
    d.update(ram_data_online_growth_verified=True,original_sceneboard_running=True,
             actual_scanout_rgb_verified=True,visually_reviewed_screen='HarmonyOS lock screen',
             desktop_verified=False,scanout_sha256=hashlib.sha256(extracts[-1][1]).hexdigest())
    return d
if __name__=='__main__':
    root=base.parent/'reports/native-original-graphics-boot-016';d=verify(root)
    with (root/'independent-verification.json').open('x') as f:json.dump(d,f,indent=2)
    print(json.dumps({k:v for k,v in d.items() if k not in ['observed_processes','dac_states','init_root_data_states']},indent=2))
