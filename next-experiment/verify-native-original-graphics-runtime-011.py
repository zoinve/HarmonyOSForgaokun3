"""Verify local storage progression, explicitly retaining unsupported-sharefs failures."""
from pathlib import Path
import json,runpy
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'verify-native-original-graphics-runtime-010.py'))['verify']
def verify(root):
 d=previous(root);r=json.loads((root/'runtime-result.json').read_text())
 s=(root/'native-logs'/r['logs'][-1]['name']).read_bytes().decode(errors='replace')
 for text in ['NATIVE_STORAGE011 local_bind_views=1','MountHmdfs: <<< EXIT SUCCESS <<< userId=100','MountByUser: <<< EXIT SUCCESS <<< userId=100','StartUser: <<< EXIT SUCCESS <<< userId=100']:
  assert text in s,text
 d.update(local_storage_user_activation=True,distributed_storage_supported=False,sharefs_supported=False,desktop_verified=False)
 return d
if __name__=='__main__':
 root=base.parent/'reports/native-original-graphics-boot-011';d=verify(root)
 with (root/'independent-verification.json').open('x') as f:json.dump(d,f,indent=2)
 print(json.dumps({k:v for k,v in d.items() if k not in ['observed_processes','dac_states','init_root_data_states','graphics_fd_rows']},indent=2))
