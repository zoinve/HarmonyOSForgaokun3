"""Validate raw evidence without equating empty trace to absent API calls."""
from pathlib import Path
import runpy,json,re
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-005.py'))['verify']
def verify(root):
    d=previous(root)
    r=json.loads((root/'runtime-result.json').read_text())
    s=(root/'native-logs'/r['logs'][-1]['name']).read_bytes().decode(errors='replace')
    sizes=re.findall(r'path=/data/native-composer-006.trace bytes=(\d+) errno=0',s)
    assert len(sizes)==12
    d.update(composer_trace_sizes=list(map(int,sizes)),composer_api_trace_observed='NATIVE_COMPOSER006' in s,
             composer_trace_absence_explained=False,desktop_verified=False)
    return d
if __name__=='__main__':
    root=base.parent/'reports/native-original-graphics-boot-006';d=verify(root)
    with (root/'independent-verification.json').open('x') as f:json.dump(d,f,indent=2)
    print(json.dumps({k:v for k,v in d.items() if k not in ['observed_processes','dac_states']},indent=2))
