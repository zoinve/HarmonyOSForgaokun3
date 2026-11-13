"""Preserve failed diagnostics as failures, not fabricated image evidence."""
from pathlib import Path
import runpy,json
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-004.py'))['verify']
def verify(root):
    d=previous(root);r=json.loads((root/'runtime-result.json').read_text())
    s=(root/'native-logs'/r['logs'][-1]['name']).read_bytes().decode(errors='replace')
    assert 'Max tag count is 10 [CODE: -42]' in s
    assert 'NATIVE_PIXELS012_BEGIN sample=11 fd=-1 errno=2' in s
    assert 'bundleInfos_ is empty' in s and 'fb=95' in s
    d.update(early_account_filter_valid=False,scanout_pixels_captured=False,bundle_database_observed_empty=True,desktop_verified=False)
    return d
if __name__=='__main__':
    root=base.parent/'reports/native-original-graphics-boot-012';d=verify(root)
    with (root/'independent-verification.json').open('x') as f:json.dump(d,f,indent=2)
    print(json.dumps({k:v for k,v in d.items() if k not in ['observed_processes','dac_states','init_root_data_states']},indent=2))
