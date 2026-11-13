"""Archive only consumed015 after independently verified012 evidence."""
from pathlib import Path
import ast,json,runpy
def launcher_source():
 s=runpy.run_path(str(Path(__file__).with_name('cleanup-consumed-diagnostic-entries-009.py')),run_name='offline_generator')['launcher_source']()
 for old,new in [('boot-entry-cleanup-009','boot-entry-cleanup-010'),
  ('baremetal-native-trial-011','baremetal-native-trial-012'),
  ("(('011', '014'),)","(('012', '015'),)"),('== 340','== 378'),
  ("for v in ('014',)","for v in ('015',)")]:
  assert old in s,old
  s=s.replace(old,new)
 ast.parse(s)
 return s
if __name__=='__main__':
 b=Path(__file__).resolve().parent.parent
 v=json.loads((b/'reports/baremetal-native-trial-012-independent-verification.json').read_text())
 assert v['raw_log_sizes_and_hashes_verified']==378 and v['one_shot_absent']
 exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
