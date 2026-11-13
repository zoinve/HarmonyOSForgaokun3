"""Validate preserved native evidence and successful early log connection."""
from pathlib import Path
import runpy,json
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-007.py'))['verify']
def verify(root):
    d=previous(root);r=json.loads((root/'runtime-result.json').read_text())
    s=(root/'native-logs'/r['logs'][-1]['name']).read_bytes().decode(errors='replace')
    assert 'Set global log level to D successfully' in s and 'CreateResponser out' in s
    d.update(early_original_hilog_connected=True,original_rs_startup_logs=True,desktop_verified=False)
    return d
if __name__=='__main__':
    root=base.parent/'reports/native-original-graphics-boot-008';d=verify(root)
    with (root/'independent-verification.json').open('x') as f:json.dump(d,f,indent=2)
    print(json.dumps({k:v for k,v in d.items() if k not in ['observed_processes','dac_states','init_root_data_states','graphics_fd_rows']},indent=2))
