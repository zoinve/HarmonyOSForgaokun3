"""Separate confirmed trace-channel activity from unobserved API calls."""
from pathlib import Path
import runpy,json,re
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-005.py'))['verify']
def verify(root):
    d=previous(root);r=json.loads((root/'runtime-result.json').read_text())
    s=(root/'native-logs'/r['logs'][-1]['name']).read_bytes().decode(errors='replace')
    rows=re.findall(r'NATIVE_COMPOSER007 pid=(\d+) uid=(\d+) call=(\w+) value=(-?\d+) errno=(\d+)',s)
    assert rows and all(x[1]=='3036' for x in rows)
    assert any(x[2]=='library_constructor' for x in rows)
    d.update(composer_trace_channel_confirmed=True,observed_composer_calls=sorted({x[2] for x in rows}),
             composer_graphics_api_observed=any(x[2]!='library_constructor' for x in rows),desktop_verified=False)
    return d
if __name__=='__main__':
    root=base.parent/'reports/native-original-graphics-boot-007';d=verify(root)
    with (root/'independent-verification.json').open('x') as f:json.dump(d,f,indent=2)
    print(json.dumps({k:v for k,v in d.items() if k not in ['observed_processes','dac_states']},indent=2))
