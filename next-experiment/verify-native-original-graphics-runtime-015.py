"""Verify actual SA511 recovery without confusing installation progress with a desktop."""
from pathlib import Path
import runpy,json
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-004.py'))['verify']
def verify(root):
    d=previous(root);r=json.loads((root/'runtime-result.json').read_text())
    s=(root/'native-logs'/r['logs'][-1]['name']).read_bytes().decode(errors='replace')
    assert 'NATIVE_LAYOUT015 path=/mnt/sandbox/system/usr/system target=/system' in s
    assert 'Scheduler SA:511 loaded' in s and 'Publish SA:511 result:0' in s
    assert '/root/usr/system/profile rc=0' in s
    assert 'errno:28' in s and 'ExtractFile' in s
    d.update(original_sa511_loaded=True,sandbox_profile_alias_verified=True,application_unpack_enospc_observed=True,desktop_verified=False)
    return d
if __name__=='__main__':
    root=base.parent/'reports/native-original-graphics-boot-015';d=verify(root)
    with (root/'independent-verification.json').open('x') as f:json.dump(d,f,indent=2)
    print(json.dumps({k:v for k,v in d.items() if k not in ['observed_processes','dac_states','init_root_data_states']},indent=2))
