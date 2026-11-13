"""Validate ashmem, original HDI and physical scanout evidence, not desktop."""
from pathlib import Path
import json,runpy
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-008.py'))['verify']
def verify(root):
    d=previous(root); r=json.loads((root/'runtime-result.json').read_text())
    s=(root/'native-logs'/r['logs'][-1]['name']).read_bytes().decode(errors='replace')
    for text in ['NATIVE_ASHMEM010 loaded=1','Init device succeed','HotPlugEvent, screenId is 0, connected is 1','Init hdiScreen succeed','call=Commit','fb=95']:
        assert text in s,text
    d.update(real_ashmem_loaded=True,original_hdi_initialized=True,real_screen_hotplug=True,composer_commit_entered=True,desktop_verified=False)
    return d
if __name__=='__main__':
    root=base.parent/'reports/native-original-graphics-boot-010';d=verify(root)
    with (root/'independent-verification.json').open('x') as f:json.dump(d,f,indent=2)
    print(json.dumps({k:v for k,v in d.items() if k not in ['observed_processes','dac_states','init_root_data_states','graphics_fd_rows']},indent=2))
