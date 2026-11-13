"""Verify real black scanout and preserve the unresolved original installd failure."""
from pathlib import Path
import runpy,json
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-004.py'))['verify']
def verify(root):
    d=previous(root);r=json.loads((root/'runtime-result.json').read_text())
    s=(root/'native-logs'/r['logs'][-1]['name']).read_bytes().decode(errors='replace')
    assert 'Max tag count is 10 [CODE: -42]' not in s
    assert 'scanout_capture_success value=95' in s
    assert 'Load system ability 511 failed with 1002' in s
    extract=runpy.run_path(str(base/'extract-native-scanout-013.py'))
    for sample in (9,11):
        data=(root/f'scanout-sample-{sample}.ppm').read_bytes()
        assert data.startswith(b'P6\n160 256\n255\n')
        assert data[15:]==bytes(160*256*3)
    d.update(scanout_pixels_captured=True,captured_scanout_black=True,installd_sa_511_load_failed=True,desktop_verified=False)
    return d
if __name__=='__main__':
    root=base.parent/'reports/native-original-graphics-boot-013';d=verify(root)
    with (root/'independent-verification.json').open('x') as f:json.dump(d,f,indent=2)
    print(json.dumps({k:v for k,v in d.items() if k not in ['observed_processes','dac_states','init_root_data_states']},indent=2))
