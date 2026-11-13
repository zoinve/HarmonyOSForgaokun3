"""Verify retained native evidence, never infer desktop from an enabled connector."""
from pathlib import Path
import runpy,json,re
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-004.py'))['verify']
def verify(root):
    d=previous(root)
    runtime=json.loads((root/'runtime-result.json').read_text())
    text=(root/'native-logs'/runtime['logs'][-1]['name']).read_bytes().decode(errors='replace')
    assert 'NATIVE_GRAPHICS005_HILOG_FOLLOW' in text
    assert 'allocated by = [fbcon]' in text
    assert re.search(r'path=/sys/class/drm/card0-DSI-1/status bytes=10 errno=0\nconnected',text)
    d.update(dsi_connected=True,retained_fbcon_scanout=True,
        graphics_fd_rows=[l for l in text.splitlines() if 'NATIVE_GRAPHICS005_FD' in l and '/dev/dri/' in l],
        original_service_stderr_null=True,desktop_verified=False)
    return d
if __name__=='__main__':
    d=verify(base.parent/'reports/native-original-graphics-boot-005')
    out=base.parent/'reports/native-original-graphics-boot-005/independent-verification.json'
    with out.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2)
    print(json.dumps({k:v for k,v in d.items() if k not in ['observed_processes','dac_states']},indent=2))
