"""Verify real HDI/ashmem failure boundary without claiming presentation."""
from pathlib import Path
import runpy,json
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-008.py'))['verify']
def verify(root):
    d=previous(root);r=json.loads((root/'runtime-result.json').read_text())
    s=(root/'native-logs'/r['logs'][-1]['name']).read_bytes().decode(errors='replace')
    for text in ['hdi device get instances failed','AshmemOpenLocked: fd is invalid, fd = -1, errno = 2','InitSMQInfo failure, ret=-3','Create DisplayCmdRequester failed 56']:
        assert text in s,text
    d.update(original_hdi_command_queue_failed=True,original_ashmem_open_errno=2,desktop_verified=False)
    return d
if __name__=='__main__':
    root=base.parent/'reports/native-original-graphics-boot-009';d=verify(root)
    with (root/'independent-verification.json').open('x') as f:json.dump(d,f,indent=2)
    print(json.dumps({k:v for k,v in d.items() if k not in ['observed_processes','dac_states','init_root_data_states','graphics_fd_rows']},indent=2))
